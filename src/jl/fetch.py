"""HTTP requests of the framework and the generators: JudaicaLink identifies itself consistently (decision 0028).

Every request sends USER_AGENT, unless a source needs another one: a generator passes user_agent=, or local.toml
names one per host (not committed, so a string given to us by a source stays private):

    [user_agent]
    "footprints.ctl.columbia.edu" = "..."

Priority: the argument, then local.toml, then USER_AGENT.
"""

import time
import urllib.error
import urllib.parse
import urllib.request

from . import config

USER_AGENT = "JudaicaLink-data (https://judaicalink.org)"

_by_host = None


def user_agent(url, override=None):
    """The User-Agent for a request to url."""
    if override:
        return override
    global _by_host
    if _by_host is None:
        try:
            table = config.load().data.get("user_agent", {})
        except config.ConfigError:
            table = {}
        _by_host = table if isinstance(table, dict) else {}
    return _by_host.get(urllib.parse.urlsplit(url).hostname or "", USER_AGENT)


def request(url, *, method=None, headers=None, data=None, agent=None):
    """A urllib Request with the User-Agent set (agent= overrides it for this request)."""
    h = dict(headers or {})
    h["User-Agent"] = user_agent(url, agent)
    return urllib.request.Request(url, data=data, headers=h, method=method)


def retry_after(e):
    """The seconds a 429/503 answer asks to wait (Retry-After in seconds), or None."""
    v = (e.headers or {}).get("Retry-After", "") if hasattr(e, "headers") else ""
    return int(v) if str(v).strip().isdigit() else None


def get(url, *, headers=None, agent=None, timeout=60, tries=6, wait=10, max_wait=900):
    """The body of url; retried with growing waits (wait, 2 x wait, ...), or as long as the server asks (Retry-After)
    when that is at most max_wait seconds (servers answer 429/503 when busy); a longer Retry-After ends at once.
    Other client errors (404, 403, ...) are raised at once as urllib.error.HTTPError."""
    for i in range(tries):
        try:
            with urllib.request.urlopen(request(url, headers=headers, agent=agent), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code < 500 and e.code != 429:
                raise
            asked = retry_after(e)
            if i + 1 == tries or (asked is not None and asked > max_wait):
                raise RuntimeError(f"failed: {url}: {e}" + (f" (Retry-After {asked} s)" if asked else "")) from e
            pause = max(asked or 0, wait * 2 ** i)
            print(f"  retry {i + 1} in {pause} s after {e}" + (f" (Retry-After {asked} s)" if asked else ""),
                  flush=True)
            time.sleep(pause)
        except Exception as e:
            if i + 1 == tries:
                raise RuntimeError(f"failed: {url}: {e}") from e
            print(f"  retry {i + 1} in {wait * 2 ** i} s after {e}", flush=True)
            time.sleep(wait * 2 ** i)
