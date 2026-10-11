#!/usr/bin/env python3
"""jl: the generator framework of judaicalink-data (decision 0018). Run ./jl --help for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from jl.cli import main  # noqa: E402

sys.exit(main())
