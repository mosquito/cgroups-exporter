import logging

from .base import CGroupTask, StatBase, gauge_factory

log = logging.getLogger()


def cpu_collector(task: CGroupTask):
    for collector in COLLECTORS:
        try:
            collector(task)()
        except Exception:
            log.exception("Failed to collect %r", collector)


class CPUAcctStat(StatBase):
    STAT_FILE = "cpuacct.stat"
    DOCUMENTATION = "CPU accounting statistic"


class CPUStat(StatBase):
    STAT_FILE = "cpu.stat"
    DOCUMENTATION = "CPU statistic"


COLLECTORS = (CPUStat, CPUAcctStat)
