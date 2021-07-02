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


COLLECTORS = (
    PIDCount,
)
