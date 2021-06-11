from aiohttp.web import Application, Request, StreamResponse
from aiomisc.service.aiohttp import AIOHTTPService
from prometheus_client import REGISTRY, Metric, CONTENT_TYPE_LATEST
from prometheus_client.utils import floatToGoString


class MetricsAPI(AIOHTTPService):
    @staticmethod
    def sample_line(line):
        if line.labels:
            labelstr = '{{{0}}}'.format(','.join(
                ['{0}="{1}"'.format(
                    k, v.replace('\\', r'\\').replace('\n', r'\n').replace('"', r'\"'))
                    for k, v in sorted(line.labels.items())]))
        else:
            labelstr = ''

        timestamp = ''
        if line.timestamp is not None:
            # Convert to milliseconds.
            timestamp = ' {0:d}'.format(int(float(line.timestamp) * 1000))
        return '{0}{1} {2}{3}\n'.format(
            line.name, labelstr, floatToGoString(line.value), timestamp)

    _TYPE_MAPPER = {
        "counter": lambda typ, name: (typ, "{}_total".format(name)),
        "info": lambda typ, name: ("gauge", "{}_info".format(name)),
        "stateset": lambda typ, name: ("gauge", name),
        "gaugehistogram": lambda typ, name: ("histogram", name),
        "unknown": lambda typ, name: ("untyped", name),
    }

    @staticmethod
    def format_help(mname, metric: Metric):
        return '# HELP {0} {1}\n'.format(
            mname,
            metric.documentation.replace(
                '\\', r'\\'
            ).replace(
                '\n', r'\n'
            )
        )

    @staticmethod
    def format_type(mname, mtype):
        return '# TYPE {0} {1}\n'.format(mname, mtype)

    def format_samples(self, metric: Metric):
        om_samples = {}

        for s in metric.samples:
            for suffix in ['_created', '_gsum', '_gcount']:
                if s.name == metric.name + suffix:
                    # OpenMetrics specific sample, put in a gauge at the end.
                    om_samples.setdefault(suffix, []).append(
                        self.sample_line(s)
                    )
                    break
            else:
                yield self.sample_line(s)

        for suffix, lines in sorted(om_samples.items()):
            yield '# HELP {0}{1} {2}\n'.format(
                metric.name, suffix,
                metric.documentation.replace('\\', r'\\').replace('\n', r'\n')
            )
            yield '# TYPE {0}{1} gauge\n'.format(metric.name, suffix)
            yield from iter(lines)

    def send_metric(self, metric: Metric):
        mapper = self._TYPE_MAPPER.get(metric.type, lambda *a: a)
        mtype, mname = mapper(metric.type, metric.name)

        yield self.format_help(mname, metric)
        yield self.format_type(mname, mtype)
        yield from self.format_samples(metric)

    async def metrics(self, request: Request):
        response = StreamResponse()
        response.content_type = CONTENT_TYPE_LATEST
        response.enable_chunked_encoding()

        await response.prepare(request)

        metric: Metric
        for metric in REGISTRY.collect():
            try:
                for line in self.send_metric(metric):
                    await response.write(line.encode())
            except Exception as exception:
                exception.args = (exception.args or ('',)) + (metric,)
                raise

        await response.write_eof()
        return response

    async def create_application(self) -> Application:
        app = Application()
        app.router.add_get("/metrics", self.metrics)
        return app
