from functools import lru_cache
from pathlib import Path
from typing import NamedTuple, Optional

from ._metrics import INF, Metric


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
    MAX_VALUE: str = "max"

    def check_inf(self, value):
        if value == self.MAX_VALUE:
            return INF

        return int(value)

    def __call__(self):
        fpath = self.task.abspath / self.FILENAME

        if not fpath.exists():
            return

        with open(fpath, "r") as fp:
            value = self.check_inf(fp.read().strip())

        metric = gauge_factory(
            self.NAME,
            self.METRIC,
            self.task.group.replace(",", "_"),
            self.DOCUMENTATION,
            labelnames=("base_path", "path"),
        )
        metric.labels(base_path=self.base_path, path=self.path).set(value)


def _normalize_name(name: Optional[str]) -> Optional[str]:
    if name is None:
        return None
    return name.replace(".", "_")


@lru_cache(2 ** 20)
def gauge_factory(
    name: str, unit: str, group, documentation: str, labelnames=(),
) -> Metric:
    return Metric(
        name=_normalize_name(name),
        help=documentation,
        labelnames=labelnames,
        namespace="cgroups",
        subsystem=_normalize_name(group),
        unit=_normalize_name(unit),
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
                    self.DOCUMENTATION + " ({!r} field from {!r} file)".format(
                        param, self.STAT_FILE,
                    ),
                    labelnames=("base_path", "path"),
                )

                metric.labels(base_path=self.base_path, path=self.path).set(
                    int(value),
                )


class PressureBase(MetricProviderBase):
    PRESSURE_FILE: str
    DOCUMENTATION: str

    def __call__(self):
        stat = self.task.abspath / self.PRESSURE_FILE
        if not stat.exists():
            return

        with open(stat, "r") as fp:
            for line in fp:
                kind, metric = line.split(" ", 1)
                metrics = {}

                for part in metric.split(" "):
                    key, value = part.split("=")
                    metrics[key] = float(value) if "." in value else int(value)

                for key, value in metrics.items():
                    doc_suffix = ""
                    if "avg" in key:
                        doc_suffix = ". Average by {} seconds".format(
                            key.split("avg", 1)[-1],
                        )
                    if "total" in key:
                        doc_suffix = " total"

                    metric = gauge_factory(
                        kind,
                        key,
                        self.PRESSURE_FILE.replace(".", "_"),
                        self.DOCUMENTATION + doc_suffix,
                        labelnames=("base_path", "path"),
                    )

                    metric.labels(
                        base_path=self.base_path,
                        path=self.path,
                    ).set(
                        value,
                    )
