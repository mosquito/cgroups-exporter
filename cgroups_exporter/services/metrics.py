from aiohttp.web import Application, Request, StreamResponse
from aiomisc import threaded_iterable
from aiomisc.service.aiohttp import AIOHTTPService

from cgroups_exporter.metrics._metrics import STORAGE


class MetricsAPI(AIOHTTPService):
    compression: bool = False

    @threaded_iterable(max_size=1024)
    def provide_metrics(self):
        for line in STORAGE:
            yield line.encode()

    async def metrics(self, request: Request):
        response = StreamResponse()
        response.content_type = "text/plain; version=0.0.4; charset=utf-8"
        response.enable_chunked_encoding()

        if self.compression:
            response.enable_compression()

        await response.prepare(request)

        async for line in self.provide_metrics():
            await response.write(line)
        await response.write_eof()
        return response

    async def create_application(self) -> Application:
        app = Application()
        app.router.add_get("/metrics", self.metrics)
        return app
