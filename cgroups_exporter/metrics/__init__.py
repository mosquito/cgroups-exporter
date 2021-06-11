from aiomisc import threaded

from .base import CGroupTask


@threaded
def metrics_handler(task: CGroupTask):
    pass
