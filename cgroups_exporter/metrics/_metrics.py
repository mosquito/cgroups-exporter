import threading
from collections import defaultdict
from typing import Dict, Iterable, NamedTuple, Union


ValueType = Union[int, float]
INF = float("inf")
MINUS_INF = float("-inf")
NaN = float("NaN")


class MetricBase:
    __slots__ = ("name", "label_names", "type", "help")

    def __init__(
        self, *, name: str, labelnames: Iterable[str], help: str = None,
        type: str = "gauge", namespace: str, subsystem: str, unit: str,
    ):
        self.name = "_".join(filter(None, (namespace, subsystem, name, unit)))
        self.help = help
        self.type = type
        self.label_names = frozenset(labelnames)


class Record(NamedTuple):
    metric: MetricBase
    labels: str

    def set(self, value: ValueType) -> None:
        STORAGE.add(self, float(value))


class Metric(MetricBase):
    def labels(self, **kwargs) -> Record:
        labels = []
        for lname in sorted(self.label_names):
            lvalue = kwargs[lname]

            if lvalue is None:
                continue

            lvalue = str(lvalue).replace('"', '\\"')
            labels.append(f"{lname}=\"{lvalue}\"")

        return Record(metric=self, labels=",".join(labels))


class Storage:
    metrics: Dict[MetricBase, Dict[Record, ValueType]]

    def __init__(self):
        self.metrics = defaultdict(dict)
        self.lock = threading.Lock()

    def add(self, record: Record, value: ValueType):
        value = float(value)
        metric = record.metric
        if metric in self.metrics and record in self.metrics[metric]:
            self.metrics[record.metric][record] = value
            return

        # prevent change when iterating
        with self.lock:
            self.metrics[metric][record] = value

    def __iter__(self):
        with self.lock:
            # make a copy of metrics to avoid slow tcp attack
            metrics = tuple(self.metrics.items())

        for metric, records in metrics:
            if metric.help:
                yield f"# HELP {metric.name} {metric.help}\n"

            if metric.type:
                yield f"# TYPE {metric.name} {metric.type}\n"

            for record, value in records.items():
                if record.labels:
                    yield "%s{%s} %.3e\n" % (
                        metric.name, record.labels, value,
                    )
                else:
                    yield "%s %.3e\n" % (metric.name, value)


STORAGE = Storage()
