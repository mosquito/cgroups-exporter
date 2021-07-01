import logging

from .base import CGroupTask, PressureBase
from .cpu import CPUStat

log = logging.getLogger()


def unified_collector(task: CGroupTask):
    for collector in COLLECTORS:
        try:
            collector(task)()
        except Exception:
            log.exception("Failed to collect %r", collector)


class UnifiedCPUPressure(PressureBase):
    PRESSURE_FILE = "cpu.pressure"
    DOCUMENTATION = "CPU resource pressure"


class UnifiedIOPressure(PressureBase):
    PRESSURE_FILE = "io.pressure"
    DOCUMENTATION = "IO resource pressure"


class UnifiedMemoryPressure(PressureBase):
    PRESSURE_FILE = "memory.pressure"
    DOCUMENTATION = "Memory resource pressure"


COLLECTORS = (
    UnifiedCPUPressure,
    UnifiedIOPressure,
    UnifiedMemoryPressure,
    CPUStat,
)
