import argparse
import os
import pwd
from random import randint

from aiomisc.log import LogFormat
from configargparse import ArgumentParser

parser = ArgumentParser(
    allow_abbrev=False,
    auto_env_var_prefix="CGROUPS_EXPORTER_",
    description="croups exporter",
    default_config_files=[
        os.path.join(os.path.expanduser("~"), ".cgroups-exporter.conf"),
        "/etc/cgroups-exporter.conf",
    ],
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    ignore_unknown_config_file_keys=True,
)

parser.add_argument(
    "-s", "--pool-size", type=int, default=2, help="Thread pool size"
)

parser.add_argument(
    "-u", "--user", required=False, help="Change process UID", type=pwd.getpwnam
)

group = parser.add_argument_group("Logging options")
group.add_argument(
    "--log-level",
    default="info",
    choices=("debug", "info", "warning", "error", "fatal"),
)
group.add_argument("--log-format", default="color", choices=LogFormat.choices())

group = parser.add_argument_group("Metrics API options")
group.add_argument("--metrics-address", default="::")
group.add_argument("--metrics-port", type=int, default=9735)

group = parser.add_argument_group("Cgroups options")
group.add_argument("--cgroups-path", nargs="+", required=True)
group.add_argument("--collector-interval", type=float, default=15.0)
group.add_argument(
    "--collector-delay", type=float, default=float(randint(1, 5))
)
group.add_argument("--collector-workers", type=int, default=4)

group = parser.add_argument_group("Profiler settings")
group.add_argument("--profiler", action="store_true")
group.add_argument("--profiler-interval", type=int, required=False, default=5)
group.add_argument(
    "--profiler-top-results",
    type=int,
    required=False,
    default=20,
)

group = parser.add_argument_group("Memory tracer settings")
group.add_argument("--memory-tracer", action="store_true")
group.add_argument(
    "--memory-tracer-interval", type=int, required=False, default=5
)
group.add_argument(
    "--memory-tracer-top-results", type=int, required=False, default=20
)
