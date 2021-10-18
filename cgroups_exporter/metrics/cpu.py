import logging

from .base import CGroupTask, IntProviderBase, StatBase


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


class CPUCFSPeriods(IntProviderBase):
    FILENAME = "cpu.cfs_period_us"
    NAME = "cfs"
    METRIC = "period_us"
    DOCUMENTATION = "Allowed CPU periods in microseconds"


class CPUCFSQuota(IntProviderBase):
    FILENAME = "cpu.cfs_quota_us"
    NAME = "cfs"
    METRIC = "quota_us"
    DOCUMENTATION = "Allowed CPU quota in microseconds"


class CPUShares(IntProviderBase):
    FILENAME = "cpu.shares"
    NAME = "shares"
    METRIC = None
    DOCUMENTATION = "Allowed CPU shares"


COLLECTORS = (
    CPUStat,
    CPUAcctStat,
    CPUCFSPeriods,
    CPUCFSQuota,
    CPUShares,
)
