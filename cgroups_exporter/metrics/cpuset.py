import logging

from .base import CGroupTask, MetricProviderBase, gauge_factory


log = logging.getLogger()


def cpuset_collector(task: CGroupTask):
    for collector in COLLECTORS:
        try:
            collector(task)()
        except Exception:
            log.exception("Failed to collect %r", collector)


class CPUSetCount(MetricProviderBase):
    STAT_FILE = "cpuset.cpus"
    DOCUMENTATION = "CPU set for the cgroup"

    def __call__(self):
        stat = self.task.abspath / self.STAT_FILE
        if not stat.exists():
            return

        with open(stat, "r") as fp:
            result = fp.read().strip().split(",")

            metric = gauge_factory(
                "count",
                "cpu",
                self.task.group.replace(",", "_"),
                self.DOCUMENTATION,
                labelnames=("base_path", "path"),
            )

            metric.labels(base_path=self.base_path, path=self.path).set(
                len(result),
            )


COLLECTORS = (
    CPUSetCount,
)
