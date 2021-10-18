import logging

from .base import CGroupTask, LimitBase, StatBase, UsageBase


log = logging.getLogger()


def memory_collector(task: CGroupTask):
    for collector in COLLECTORS:
        try:
            collector(task)()
        except Exception:
            log.exception("Failed to collect %r", collector)


class MemoryKernelMaxUsage(UsageBase):
    FILENAME = "memory.kmem.max_usage_in_bytes"
    METRIC = "kmem_max"
    DOCUMENTATION = "Maximum kernel memory usage"


class MemoryKernelTCPUsage(UsageBase):
    FILENAME = "memory.kmem.tcp.usage_in_bytes"
    METRIC = "kmem_tcp"
    DOCUMENTATION = "Kernel TCP memory usage"


class MemoryKernelTCPMaxUsage(UsageBase):
    FILENAME = "memory.kmem.usage_in_bytes"
    METRIC = "kmem"
    DOCUMENTATION = "Maximum kernel TCP maximum memory usage"


class MemoryMaxUsage(UsageBase):
    FILENAME = "memory.max_usage_in_bytes"
    METRIC = "max"
    DOCUMENTATION = "Maximum memory usage"


class MemorySwapMaxUsage(UsageBase):
    FILENAME = "memory.memsw.max_usage_in_bytes"
    METRIC = "swap_max"
    DOCUMENTATION = "Maximum swap usage"


class MemorySwapUsage(UsageBase):
    FILENAME = "memory.memsw.usage_in_bytes"
    METRIC = "swap"
    DOCUMENTATION = "Swap usage"


class MemoryUsage(UsageBase):
    FILENAME = "memory.usage_in_bytes"
    METRIC = None
    DOCUMENTATION = "Memory usage"


class MemoryKernelLimit(LimitBase):
    FILENAME = "memory.kmem.limit_in_bytes"
    METRIC = "kmem"
    DOCUMENTATION = "Memory kernel limit"


class MemoryKernelTCPLimit(LimitBase):
    FILENAME = "memory.kmem.tcp.limit_in_bytes"
    METRIC = "kmem_tcp"
    DOCUMENTATION = "Kernel TCP memory limit"


class MemoryLimit(LimitBase):
    FILENAME = "memory.limit_in_bytes"
    METRIC = None
    DOCUMENTATION = "Memory limit"


class MemorySwapLimit(LimitBase):
    FILENAME = "memory.memsw.limit_in_bytes"
    METRIC = "swap"
    DOCUMENTATION = "Swap limit"


class MemorySoftLimit(LimitBase):
    FILENAME = "memory.soft_limit_in_bytes"
    METRIC = "soft"
    DOCUMENTATION = "Soft limit"


class MemoryStatProvider(StatBase):
    STAT_FILE = "memory.stat"
    DOCUMENTATION = "memory statistic"


COLLECTORS = (
    MemoryKernelMaxUsage,
    MemoryKernelTCPUsage,
    MemoryKernelTCPMaxUsage,
    MemoryMaxUsage,
    MemorySwapMaxUsage,
    MemorySwapUsage,
    MemoryUsage,
    MemoryKernelLimit,
    MemoryKernelTCPLimit,
    MemoryLimit,
    MemorySwapLimit,
    MemorySoftLimit,
    MemoryStatProvider,
)
