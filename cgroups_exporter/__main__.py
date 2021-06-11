import logging
import os

from aiomisc import entrypoint
from aiomisc.log import basic_config
from aiomisc.service import Profiler, MemoryTracer

from cgroups_exporter.args import parser
from cgroups_exporter.services.collector import Collector
from cgroups_exporter.services.metrics import MetricsAPI


def main():
    arguments = parser.parse_args()

    log_config = dict(
        log_level=arguments.log_level,
        log_format=arguments.log_format,
    )

    basic_config(**log_config)

    services = [
        MetricsAPI(
            address=arguments.metrics_address,
            port=arguments.metrics_port
        ),
        Collector(
            interval=arguments.collector_interval,
            delay=arguments.collector_delay,
            cgroup_paths=arguments.cgroups_path,
            max_workers=arguments.collector_workers,
        )
    ]

    if arguments.profiler:
        services.append(
            Profiler(
                interval=arguments.profiler_interval,
                top_results=arguments.profiler_top_results,
            ),
        )

    if arguments.memory_tracer:
        services.append(
            MemoryTracer(
                interval=arguments.memory_tracer_interval,
                top_results=arguments.memory_tracer_top_results,
            ),
        )

    entrypoint_kw = dict(pool_size=arguments.pool_size)

    with entrypoint(*services, **log_config, **entrypoint_kw) as loop:
        logging.info("CGroups exporter has been started")
        if arguments.user is not None:
            logging.info("Changing user to %r", arguments.user.pw_name)
            os.setgid(arguments.user.pw_gid)
            os.setuid(arguments.user.pw_uid)
        loop.run_forever()


if __name__ == "__main__":
    main()
