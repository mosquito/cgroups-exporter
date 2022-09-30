import io
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import IO

from aiomisc import threaded

from .base import gauge_factory


log = logging.getLogger()


@threaded
def meminfo():
    for collector in COLLECTORS:
        try:
            collector()()
        except Exception:
            log.exception("Failed to collect %r", collector)


@lru_cache(None)
def snake_case(camel_case: str) -> str:
    with io.StringIO() as fp:
        for letter in camel_case:
            if letter.isupper():
                fp.write("_")
                fp.write(letter.lower())
            else:
                fp.write(letter)
        return fp.getvalue().strip("_")


class MemInfo:
    _METRIC_REGEXP = re.compile(
        r"^(?P<name>[^[\(]+)(\((?P<label>\S+)\))?:\s*"
        r"(?P<value>\d+)(\s?(?P<suffix>\S+))?$",
    )

    SUFFIXES = ("", "k", "m", "g", "t", "p", "e")

    def parse_file(self, fp: IO[str]):
        for line in fp:
            match = self._METRIC_REGEXP.match(line)
            if match is None:
                log.debug("Skip line %r", line)
                continue

            parsed = match.groupdict()
            name = parsed.get("name")
            value = parsed.get("value")
            label = parsed.get("label")
            suffix = (parsed.get("suffix") or "").lower()[:1]

            if not value.isdigit() or suffix not in self.SUFFIXES:
                continue

            multiplier = 1024 ** self.SUFFIXES.index(suffix)
            documentation = f"{name} field from /proc/meminfo"
            yield (
                snake_case(name), int(value) * multiplier, label, documentation,
            )

    def __call__(self):
        meminfo_path = Path("/proc/meminfo")
        if not meminfo_path.is_file():
            return

        with open(meminfo_path, "r") as fp:
            for name, value, label, doc in self.parse_file(fp):
                args = ("meminfo", name, "host", doc)
                if label:
                    gauge_factory(*args, labelnames=("kind",)).labels(
                        kind=label,
                    ).set(value)

                else:
                    gauge_factory(*args).labels().set(value)


COLLECTORS = (
    MemInfo,
)
