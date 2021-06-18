import logging
from types import MappingProxyType

from aiomisc import threaded

from .base import CGroupTask
from .memory import memory_collector
from .blkio import blkio_collector

log = logging.getLogger(__name__)

HANDLER_REGISTRY = MappingProxyType({
    "memory": memory_collector,
    "blkio": blkio_collector,
})


@threaded
def metrics_handler(task: CGroupTask):
    def log_unhandled(task):
        log.debug("Unhandled metric group %r", task.group)

    HANDLER_REGISTRY.get(task.group, log_unhandled)(task)
