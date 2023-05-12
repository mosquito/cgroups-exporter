import pwd
from pathlib import Path
from random import randint
from typing import Iterable

import argclass
from aiomisc.log import LogFormat
from aiomisc_log import LogLevel


class LogGroup(argclass.Group):
    level: str = argclass.Argument(choices=LogLevel.choices())
    format: str = argclass.Argument(choices=LogFormat.choices())


class MetricsGroup(argclass.Group):
    address: str = "::"
    port: int = 9753
    disable_compression: bool = False


class CgroupGroup(argclass.Group):
    path: Iterable[str] = argclass.Argument(
        nargs=argclass.Nargs.ONE_OR_MORE, required=True,
    )
    root: Path = Path("/sys/fs/cgroup")


class CollectorGroup(argclass.Group):
    interval: int = 15
    delay: int = randint(1, 5)
    workers: int = 4


class TracerGroup(argclass.Group):
    enable: bool = False
    top_results: int = 20
    interval: int = 5


class Parser(argclass.Parser):
    pool_size: int = argclass.Argument(
        "-s", default=4,
        help="Thread pool size",
    )
    user: pwd.struct_passwd = argclass.Argument(
        "-u", required=False,
        help="Change process UID",
        type=pwd.getpwnam,
    )
    log = LogGroup(
        defaults=dict(
            level=LogLevel.default(),
            format=LogFormat.default(),
        ),
    )

    metrics = MetricsGroup(title="Metrics options")
    cgroups = CgroupGroup(title="CGroups options")
    collector = CollectorGroup(title="Collector options")
    profiler = TracerGroup(title="Profiler options")
    memory_tracer = TracerGroup(title="Memory Tracer options")
