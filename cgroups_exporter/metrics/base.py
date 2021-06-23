from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

from prometheus_client import Gauge


class CGroupTask(NamedTuple):
    abspath: Path
    base: Path
    group: str
    path: Path


class MetricProviderBase:
    def __init__(self, task: CGroupTask):
        self.task = task
        self.base_path = str(task.base)
        self.path = str(task.path)

    def __call__(self):
        raise NotImplementedError


class IntProviderBase(MetricProviderBase):
    FILENAME: str
    NAME: str
    METRIC: str
    DOCUMENTATION: str

    def __call__(self):
        fpath = self.task.abspath / self.FILENAME

        if not fpath.exists():
            return

        with open(fpath, "r") as fp:
            value = int(fp.read())

        metric = gauge_factory(
            self.NAME,
            self.METRIC,
            self.task.group,
            self.DOCUMENTATION,
            labelnames=("base_path", "path"),
        )
        metric.labels(base_path=self.base_path, path=self.path).set(value)


@lru_cache
def gauge_factory(
    name: str, unit: str, group, documentation: str, labelnames=()
) -> Gauge:
    return Gauge(
        name=name,
        documentation=documentation,
        labelnames=labelnames,
        namespace="cgroups",
        subsystem=group,
        unit=unit,
    )


class UsageBase(IntProviderBase):
    NAME = "usage"


class LimitBase(IntProviderBase):
    NAME = "limit"


class StatBase(MetricProviderBase):
    STAT_FILE: str
    DOCUMENTATION: str

    def __call__(self):
        stat = self.task.abspath / self.STAT_FILE
        if not stat.exists():
            return

        with open(stat, "r") as fp:
            for line in fp:
                param, value = line.strip().split(" ", 1)
                metric = gauge_factory(
                    "stat",
                    param,
                    self.task.group.replace(",", "_"),
                    self.DOCUMENTATION,
                    labelnames=("base_path", "path"),
                )

                metric.labels(base_path=self.base_path, path=self.path).set(
                    int(value)
                )
