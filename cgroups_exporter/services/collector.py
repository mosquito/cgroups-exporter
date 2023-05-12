import asyncio
import glob
import logging
import os
import re
from pathlib import Path
from typing import Any, Iterable

from aiochannel import Channel
from aiomisc import threaded_iterable_separate
from aiomisc.service.periodic import PeriodicService

from cgroups_exporter.metrics import (
    HANDLER_REGISTRY, CGroupTask, metrics_handler,
)
from cgroups_exporter.metrics.blkio import uptade_device_ids
from cgroups_exporter.metrics.meminfo import meminfo


log = logging.getLogger(__name__)


class Collector(PeriodicService):
    __required__ = ("cgroup_paths",)

    cgroup_paths: Iterable[str]
    max_workers: int = 8

    groups = tuple(HANDLER_REGISTRY.keys())

    SPLIT_EXP = re.compile(
        r"^(?P<base>.*)/(?P<group>{0})/(?P<path>.*)/?$".format("|".join(groups)),

    )

    @threaded_iterable_separate(max_size=1024)
    def resolve_paths(self):
        for path_glob in self.cgroup_paths:
            for path in glob.glob(path_glob, recursive=True):

                if not os.path.isdir(path):
                    log.debug("Is not directory path %r skipping...", path)
                    continue

                log.debug("Processing path %s", path)

                match = self.SPLIT_EXP.match(path)

                if match is None:
                    continue

                data = match.groupdict()
                log.debug("Parsed %r", data)
                yield CGroupTask(
                    abspath=Path(path),
                    base=Path(data["base"]),
                    group=data["group"],
                    path=Path(data["path"]),
                )

    async def producer(self, channel: Channel):
        async for path in self.resolve_paths():
            await channel.put(path)
        channel.close()

    async def worker(self, channel):
        async for task in channel:
            try:
                await metrics_handler(task)
            except Exception:
                log.exception("Failed to handle metric %r", task)

    async def callback(self) -> Any:
        log.debug("Starting to collect metrics")
        await meminfo()

        channel = Channel(maxsize=self.max_workers * 2)
        tasks = [self.producer(channel)]

        for _ in range(self.max_workers):
            tasks.append(self.worker(channel))

        await self.before_collect()
        await asyncio.gather(*tasks)

    async def before_collect(self):
        await uptade_device_ids()

