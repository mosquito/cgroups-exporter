from pathlib import Path
from typing import NamedTuple


class CGroupTask(NamedTuple):
    abspath: Path
    base: Path
    group: str
    path: Path
