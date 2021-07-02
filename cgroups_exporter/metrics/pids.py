import logging

from .base import CGroupTask, IntProviderBase

log = logging.getLogger()


def pids_collector(task: CGroupTask):
    for collector in COLLECTORS:
        try:
            collector(task)()
        except Exception:
            log.exception("Failed to collect %r", collector)


class PIDCount(IntProviderBase):
    FILENAME = "pids.current"
    DOCUMENTATION = "Process IDs count for this namespace"
    NAME = "count"
    METRIC = None


class PIDMax(IntProviderBase):
    FILENAME = "pids.max"
    DOCUMENTATION = "Maximum Process IDs allowed for this namespace"
    NAME = "max"
    METRIC = None


COLLECTORS = (
    PIDCount,
    PIDMax,
)
