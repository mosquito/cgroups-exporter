import logging
from abc import ABC
from glob import glob
from pathlib import Path
from types import MappingProxyType
from typing import Tuple

from aiomisc import threaded

from .base import CGroupTask, MetricProviderBase, gauge_factory


log = logging.getLogger()


def block_device_ids() -> Tuple[str, Path]:
    path: Path
    sys_dev_path = Path("/dev")
    base = Path("/sys/block")
    for path in map(Path, glob(str(base / "**/"))):
        dev_path = path / "dev"
        dm_path = path / "dm" / "name"

        if not dev_path.exists():
            continue

        with open(dev_path) as fp:
            dev_id = fp.read().strip()

        device_path = path.relative_to(base)
        if dm_path.exists():
            with open(dm_path) as fp:
                device_path = sys_dev_path / "mapper" / fp.read().strip()

        yield dev_id, device_path


DEVICE_IDS = {}


@threaded
def uptade_device_ids():
    global DEVICE_IDS
    DEVICE_IDS = MappingProxyType(dict(block_device_ids()))


def blkio_collector(task: CGroupTask):
    for collector in COLLECTORS:
        try:
            collector(task)()
        except Exception:
            log.exception("Failed to collect %r", collector)


class BlockIOBase(MetricProviderBase, ABC):
    FILENAME: str
    NAME: str
    DOCUMENTATION: str

    def __call__(self, *args, **kwargs):
        path = self.task.abspath / self.FILENAME

        if not path.exists():
            return

        with open(path, "r") as fp:
            for line in fp:
                if line.startswith("Total"):
                    metric_name, value = line.split()
                    device = None
                else:
                    device_id, metric_name, value = line.split()
                    device = DEVICE_IDS[device_id]

                metric_name = metric_name.lower()

                metric = gauge_factory(
                    self.NAME,
                    metric_name,
                    self.task.group,
                    self.DOCUMENTATION + " ({!r} field from {!r} file)".format(
                        metric_name, self.FILENAME,
                    ),
                    labelnames=("base_path", "path", "device"),
                )

                metric.labels(
                    base_path=self.base_path, path=self.path, device=device,
                ).set(value)


class BlockIOBFQServiceBytesRecursive(BlockIOBase):
    FILENAME = "blkio.bfq.io_service_bytes_recursive"
    NAME = "bfq_service_bytes_recursive"
    DOCUMENTATION = "BlockIO service bytes recursive"


class BlockIOBFQServiceBytes(BlockIOBase):
    FILENAME = "blkio.bfq.io_service_bytes"
    NAME = "bfq_service_bytes"
    DOCUMENTATION = "BlockIO service bytes"


class BlockIOBFQServicedRecursive(BlockIOBase):
    FILENAME = "blkio.bfq.io_serviced_recursive"
    NAME = "bfq_serviced_recursive"
    DOCUMENTATION = "BlockIO serviced bytes recursive"


class BlockIOBFQServiced(BlockIOBase):
    FILENAME = "blkio.bfq.io_serviced"
    NAME = "bfq_serviced"
    DOCUMENTATION = "BlockIO serviced bytes"


class BlockIOThrottleServiceBytesRecursive(BlockIOBase):
    FILENAME = "blkio.throttle.io_service_bytes_recursive"
    NAME = "throttle_service_bytes_recursive"
    DOCUMENTATION = "BlockIO throttle serviced bytes"


class BlockIOThrottleServiceBytes(BlockIOBase):
    FILENAME = "blkio.throttle.io_service_bytes"
    NAME = "throttle_service_bytes"
    DOCUMENTATION = "BlockIO service bytes"


class BlockIOThrottleServicedRecursive(BlockIOBase):
    FILENAME = "blkio.throttle.io_serviced_recursive"
    NAME = "throttle_serviced_recursive"
    DOCUMENTATION = "BlockIO serviced bytes recursive"


class BlockIOThrottleServiced(BlockIOBase):
    FILENAME = "blkio.throttle.io_serviced"
    NAME = "throttle_serviced"
    DOCUMENTATION = "BlockIO serviced bytes"


COLLECTORS = (
    BlockIOBFQServiceBytes,
    BlockIOBFQServiceBytesRecursive,
    BlockIOBFQServiced,
    BlockIOBFQServicedRecursive,
    BlockIOThrottleServiceBytes,
    BlockIOThrottleServiceBytesRecursive,
    BlockIOThrottleServiced,
    BlockIOThrottleServicedRecursive,
)
