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


def get(url, *, headers=None, agent=None, timeout=60, tries=5, wait=10):
    """The body of url; retried with growing waits (servers answer 429/503 when busy). Other client errors
    (404, 403, ...) are raised at once as urllib.error.HTTPError."""
    for i in range(tries):
        try:
            with urllib.request.urlopen(request(url, headers=headers, agent=agent), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code < 500 and e.code != 429:
                raise
            if i + 1 == tries:
                raise RuntimeError(f"failed: {url}: {e}") from e
            print(f"  retry {i + 1} after {e}", flush=True)
            time.sleep(wait * (i + 1))
        except Exception as e:
            if i + 1 == tries:
                raise RuntimeError(f"failed: {url}: {e}") from e
            print(f"  retry {i + 1} after {e}", flush=True)
            time.sleep(wait * (i + 1))
