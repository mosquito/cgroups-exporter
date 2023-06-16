CGroups exporter
================

Exporter for CGroups metrics, for LXD/Docker/systemd. 

Collects metrics for all cgroups based containers or SystemD services 
on the host machine, without the need to install separate exporters 
inside each container.

Installation
------------

```bash
pip install cgroups-exporter
```

Example
-------

A simple example collects all available metrics for LXD containers.

```bash
cgroups-exporter --cgroups-path "/sys/fs/cgroup/*/lxc.payload.*"
```

You can pass several path templates, then metrics will be collected from everyone.

In the example below, metrics will be collected for:
* All LXD containers
* All SystemD services running inside the LXD containers
* All Docker containers inside the LXD containers.
* All user slices (when used entering through the ssh the 
  SystemD creates the slice named by template `user-$UID`)

```bash
cgroups-exporter \
  --cgroups-path \
      "/sys/fs/cgroup/*/lxc.payload.*/" \
      "/sys/fs/cgroup/unified/lxc.payload.*/**/*.service" \
      "/sys/fs/cgroup/unified/lxc.payload.*/**/user-*" \
      "/sys/fs/cgroup/cpu/lxc.payload.*/**/*.service" \
      "/sys/fs/cgroup/unified/**/user.slice/user-*" \
      "/sys/fs/cgroup/*/lxc.payload.*/docker/*"
```

Usage
-----

Args that start with `--` (eg. -s) can also be set in a config file 
(`~/.cgroups-exporter.conf` or `/etc/cgroups-exporter.conf`). 

Config file syntax allows: `key=value`, `flag=true`, `stuff=[a,b,c]` 
(for details, see syntax [here](https://goo.gl/R74nmi)). 

If an arg is specified in more than one place, then commandline values 
override environment variables which override config file values 
which override defaults.

Environment variable `CGROUPS_EXPORTER_CONFIG` overwrites config file location.

```
usage: cgroups-exporter [-h] [-s POOL_SIZE] [-u USER] [--log-level {critical,error,warning,info,debug,notset}] [--log-format {stream,color,json,syslog,plain,journald,rich,rich_tb}] [--metrics-address METRICS_ADDRESS]
                        [--metrics-port METRICS_PORT] [--metrics-disable-compression] --cgroups-path CGROUPS_PATH [CGROUPS_PATH ...] [--cgroups-root CGROUPS_ROOT] [--collector-interval COLLECTOR_INTERVAL]
                        [--collector-delay COLLECTOR_DELAY] [--collector-workers COLLECTOR_WORKERS] [--profiler-enable] [--profiler-top-results PROFILER_TOP_RESULTS] [--profiler-interval PROFILER_INTERVAL] [--memory-tracer-enable]
                        [--memory-tracer-top-results MEMORY_TRACER_TOP_RESULTS] [--memory-tracer-interval MEMORY_TRACER_INTERVAL]

croups exporter

options:
  -h, --help            show this help message and exit
  -s POOL_SIZE          Thread pool size (default: 4) [ENV: CGROUPS_EXPORTER_POOL_SIZE]
  -u USER               Change process UID [ENV: CGROUPS_EXPORTER_USER]

  --log-level {critical,error,warning,info,debug,notset}
                        (default: info) [ENV: CGROUPS_EXPORTER_LOG_LEVEL]
  --log-format {stream,color,json,syslog,plain,journald,rich,rich_tb}
                        (default: color) [ENV: CGROUPS_EXPORTER_LOG_FORMAT]

Metrics options:
  --metrics-address METRICS_ADDRESS
                        (default: ::) [ENV: CGROUPS_EXPORTER_METRICS_ADDRESS]
  --metrics-port METRICS_PORT
                        (default: 9753) [ENV: CGROUPS_EXPORTER_METRICS_PORT]
  --metrics-disable-compression
                        [ENV: CGROUPS_EXPORTER_METRICS_DISABLE_COMPRESSION]

CGroups options:
  --cgroups-path CGROUPS_PATH [CGROUPS_PATH ...]
                        [ENV: CGROUPS_EXPORTER_CGROUPS_PATH]
  --cgroups-root CGROUPS_ROOT
                        (default: /sys/fs/cgroup) [ENV: CGROUPS_EXPORTER_CGROUPS_ROOT]

Collector options:
  --collector-interval COLLECTOR_INTERVAL
                        (default: 15) [ENV: CGROUPS_EXPORTER_COLLECTOR_INTERVAL]
  --collector-delay COLLECTOR_DELAY
                        (default: 4) [ENV: CGROUPS_EXPORTER_COLLECTOR_DELAY]
  --collector-workers COLLECTOR_WORKERS
                        (default: 4) [ENV: CGROUPS_EXPORTER_COLLECTOR_WORKERS]

Profiler options:
  --profiler-enable     [ENV: CGROUPS_EXPORTER_PROFILER_ENABLE]
  --profiler-top-results PROFILER_TOP_RESULTS
                        (default: 20) [ENV: CGROUPS_EXPORTER_PROFILER_TOP_RESULTS]
  --profiler-interval PROFILER_INTERVAL
                        (default: 5) [ENV: CGROUPS_EXPORTER_PROFILER_INTERVAL]

Memory Tracer options:
  --memory-tracer-enable
                        [ENV: CGROUPS_EXPORTER_MEMORY_TRACER_ENABLE]
  --memory-tracer-top-results MEMORY_TRACER_TOP_RESULTS
                        (default: 20) [ENV: CGROUPS_EXPORTER_MEMORY_TRACER_TOP_RESULTS]
  --memory-tracer-interval MEMORY_TRACER_INTERVAL
                        (default: 5) [ENV: CGROUPS_EXPORTER_MEMORY_TRACER_INTERVAL]

Default values will based on following configuration files ['cgroups-exporter.conf', '~/.cgroups-exporter.conf', '/etc/cgroups-exporter.conf']. The configuration files is INI-formatted files where configuration groups is INI
sections.See more https://pypi.org/project/argclass/#configs
```

Container Usage
---------------

`cgroups-exporter` is also available as a container image to be used in Docker, Kubernetes or other runtimes. It expects the host `/sys` directory to be mounted in the container (read only).

Docker usage example:

```shell
docker run -p 9753:9753 -v /sys/:/host_sys/ ghcr.io/mosquito/cgroups-exporter:latest cgroups-exporter --cgroups-path "/host_sys/fs/cgroup/*/docker/*"
```


Metrics
-------

| Name | Description |
| ------------ | ------------ |
| `cgroups_blkio_bfq_service_bytes_async` | BlockIO service bytes ('async' field from 'blkio.bfq.io_service_bytes' file) |
| `cgroups_blkio_bfq_service_bytes_discard` | BlockIO service bytes ('discard' field from 'blkio.bfq.io_service_bytes' file) |
| `cgroups_blkio_bfq_service_bytes_read` | BlockIO service bytes ('read' field from 'blkio.bfq.io_service_bytes' file) |
| `cgroups_blkio_bfq_service_bytes_recursive_async` | BlockIO service bytes recursive ('async' field from 'blkio.bfq.io_service_bytes_recursive' file) |
| `cgroups_blkio_bfq_service_bytes_recursive_discard` | BlockIO service bytes recursive ('discard' field from 'blkio.bfq.io_service_bytes_recursive' file) |
| `cgroups_blkio_bfq_service_bytes_recursive_read` | BlockIO service bytes recursive ('read' field from 'blkio.bfq.io_service_bytes_recursive' file) |
| `cgroups_blkio_bfq_service_bytes_recursive_sync` | BlockIO service bytes recursive ('sync' field from 'blkio.bfq.io_service_bytes_recursive' file) |
| `cgroups_blkio_bfq_service_bytes_recursive_total` | BlockIO service bytes recursive ('total' field from 'blkio.bfq.io_service_bytes_recursive' file) |
| `cgroups_blkio_bfq_service_bytes_recursive_write` | BlockIO service bytes recursive ('write' field from 'blkio.bfq.io_service_bytes_recursive' file) |
| `cgroups_blkio_bfq_service_bytes_sync` | BlockIO service bytes ('sync' field from 'blkio.bfq.io_service_bytes' file) |
| `cgroups_blkio_bfq_service_bytes_total` | BlockIO service bytes ('total' field from 'blkio.bfq.io_service_bytes' file) |
| `cgroups_blkio_bfq_service_bytes_write` | BlockIO service bytes ('write' field from 'blkio.bfq.io_service_bytes' file) |
| `cgroups_blkio_bfq_serviced_async` | BlockIO serviced bytes ('async' field from 'blkio.bfq.io_serviced' file) |
| `cgroups_blkio_bfq_serviced_discard` | BlockIO serviced bytes ('discard' field from 'blkio.bfq.io_serviced' file) |
| `cgroups_blkio_bfq_serviced_read` | BlockIO serviced bytes ('read' field from 'blkio.bfq.io_serviced' file) |
| `cgroups_blkio_bfq_serviced_recursive_async` | BlockIO serviced bytes recursive ('async' field from 'blkio.bfq.io_serviced_recursive' file) |
| `cgroups_blkio_bfq_serviced_recursive_discard` | BlockIO serviced bytes recursive ('discard' field from 'blkio.bfq.io_serviced_recursive' file) |
| `cgroups_blkio_bfq_serviced_recursive_read` | BlockIO serviced bytes recursive ('read' field from 'blkio.bfq.io_serviced_recursive' file) |
| `cgroups_blkio_bfq_serviced_recursive_sync` | BlockIO serviced bytes recursive ('sync' field from 'blkio.bfq.io_serviced_recursive' file) |
| `cgroups_blkio_bfq_serviced_recursive_total` | BlockIO serviced bytes recursive ('total' field from 'blkio.bfq.io_serviced_recursive' file) |
| `cgroups_blkio_bfq_serviced_recursive_write` | BlockIO serviced bytes recursive ('write' field from 'blkio.bfq.io_serviced_recursive' file) |
| `cgroups_blkio_bfq_serviced_sync` | BlockIO serviced bytes ('sync' field from 'blkio.bfq.io_serviced' file) |
| `cgroups_blkio_bfq_serviced_total` | BlockIO serviced bytes ('total' field from 'blkio.bfq.io_serviced' file) |
| `cgroups_blkio_bfq_serviced_write` | BlockIO serviced bytes ('write' field from 'blkio.bfq.io_serviced' file) |
| `cgroups_blkio_throttle_service_bytes_async` | BlockIO service bytes ('async' field from 'blkio.throttle.io_service_bytes' file) |
| `cgroups_blkio_throttle_service_bytes_discard` | BlockIO service bytes ('discard' field from 'blkio.throttle.io_service_bytes' file) |
| `cgroups_blkio_throttle_service_bytes_read` | BlockIO service bytes ('read' field from 'blkio.throttle.io_service_bytes' file) |
| `cgroups_blkio_throttle_service_bytes_recursive_async` | BlockIO throttle serviced bytes ('async' field from 'blkio.throttle.io_service_bytes_recursive' file) |
| `cgroups_blkio_throttle_service_bytes_recursive_discard` | BlockIO throttle serviced bytes ('discard' field from 'blkio.throttle.io_service_bytes_recursive' file) |
| `cgroups_blkio_throttle_service_bytes_recursive_read` | BlockIO throttle serviced bytes ('read' field from 'blkio.throttle.io_service_bytes_recursive' file) |
| `cgroups_blkio_throttle_service_bytes_recursive_sync` | BlockIO throttle serviced bytes ('sync' field from 'blkio.throttle.io_service_bytes_recursive' file) |
| `cgroups_blkio_throttle_service_bytes_recursive_total` | BlockIO throttle serviced bytes ('total' field from 'blkio.throttle.io_service_bytes_recursive' file) |
| `cgroups_blkio_throttle_service_bytes_recursive_write` | BlockIO throttle serviced bytes ('write' field from 'blkio.throttle.io_service_bytes_recursive' file) |
| `cgroups_blkio_throttle_service_bytes_sync` | BlockIO service bytes ('sync' field from 'blkio.throttle.io_service_bytes' file) |
| `cgroups_blkio_throttle_service_bytes_total` | BlockIO service bytes ('total' field from 'blkio.throttle.io_service_bytes' file) |
| `cgroups_blkio_throttle_service_bytes_write` | BlockIO service bytes ('write' field from 'blkio.throttle.io_service_bytes' file) |
| `cgroups_blkio_throttle_serviced_async` | BlockIO serviced bytes ('async' field from 'blkio.throttle.io_serviced' file) |
| `cgroups_blkio_throttle_serviced_discard` | BlockIO serviced bytes ('discard' field from 'blkio.throttle.io_serviced' file) |
| `cgroups_blkio_throttle_serviced_read` | BlockIO serviced bytes ('read' field from 'blkio.throttle.io_serviced' file) |
| `cgroups_blkio_throttle_serviced_recursive_async` | BlockIO serviced bytes recursive ('async' field from 'blkio.throttle.io_serviced_recursive' file) |
| `cgroups_blkio_throttle_serviced_recursive_discard` | BlockIO serviced bytes recursive ('discard' field from 'blkio.throttle.io_serviced_recursive' file) |
| `cgroups_blkio_throttle_serviced_recursive_read` | BlockIO serviced bytes recursive ('read' field from 'blkio.throttle.io_serviced_recursive' file) |
| `cgroups_blkio_throttle_serviced_recursive_sync` | BlockIO serviced bytes recursive ('sync' field from 'blkio.throttle.io_serviced_recursive' file) |
| `cgroups_blkio_throttle_serviced_recursive_total` | BlockIO serviced bytes recursive ('total' field from 'blkio.throttle.io_serviced_recursive' file) |
| `cgroups_blkio_throttle_serviced_recursive_write` | BlockIO serviced bytes recursive ('write' field from 'blkio.throttle.io_serviced_recursive' file) |
| `cgroups_blkio_throttle_serviced_sync` | BlockIO serviced bytes ('sync' field from 'blkio.throttle.io_serviced' file) |
| `cgroups_blkio_throttle_serviced_total` | BlockIO serviced bytes ('total' field from 'blkio.throttle.io_serviced' file) |
| `cgroups_blkio_throttle_serviced_write` | BlockIO serviced bytes ('write' field from 'blkio.throttle.io_serviced' file) |
| `cgroups_cpu_cpuacct_cfs_period_us` | Allowed CPU periods in microseconds |
| `cgroups_cpu_cpuacct_cfs_quota_us` | Allowed CPU quota in microseconds |
| `cgroups_cpu_cpuacct_shares` | Allowed CPU shares |
| `cgroups_cpu_cpuacct_stat_nr_periods` | CPU statistic ('nr_periods' field from 'cpu.stat' file) |
| `cgroups_cpu_cpuacct_stat_nr_throttled` | CPU statistic ('nr_throttled' field from 'cpu.stat' file) |
| `cgroups_cpu_cpuacct_stat_system` | CPU accounting statistic ('system' field from 'cpuacct.stat' file) |
| `cgroups_cpu_cpuacct_stat_throttled_time` | CPU statistic ('throttled_time' field from 'cpu.stat' file) |
| `cgroups_cpu_cpuacct_stat_user` | CPU accounting statistic ('user' field from 'cpuacct.stat' file) |
| `cgroups_cpu_pressure_some_avg10` | CPU resource pressure. Average by 10 seconds |
| `cgroups_cpu_pressure_some_avg300` | CPU resource pressure. Average by 300 seconds |
| `cgroups_cpu_pressure_some_avg60` | CPU resource pressure. Average by 60 seconds |
| `cgroups_cpu_pressure_some_total` | CPU resource pressure total |
| `cgroups_cpuset_count_cpu` | CPU set for the cgroup |
| `cgroups_exporter_calls_collector_created` | Exporter collector run counter |
| `cgroups_exporter_calls_collector_total` | Exporter collector run counter |
| `cgroups_exporter_collect_time_collector_created` | Exporter collector execution time |
| `cgroups_exporter_collect_time_collector` | Exporter collector execution time |
| `cgroups_io_pressure_full_avg10` | IO resource pressure. Average by 10 seconds |
| `cgroups_io_pressure_full_avg300` | IO resource pressure. Average by 300 seconds |
| `cgroups_io_pressure_full_avg60` | IO resource pressure. Average by 60 seconds |
| `cgroups_io_pressure_full_total` | IO resource pressure total |
| `cgroups_io_pressure_some_avg10` | IO resource pressure. Average by 10 seconds |
| `cgroups_io_pressure_some_avg300` | IO resource pressure. Average by 300 seconds |
| `cgroups_io_pressure_some_avg60` | IO resource pressure. Average by 60 seconds |
| `cgroups_io_pressure_some_total` | IO resource pressure total |
| `cgroups_memory_limit_kmem_tcp` | Kernel TCP memory limit |
| `cgroups_memory_limit_kmem` | Memory kernel limit |
| `cgroups_memory_limit_soft` | Soft limit |
| `cgroups_memory_limit_swap` | Swap limit |
| `cgroups_memory_limit` | Memory limit |
| `cgroups_memory_pressure_full_avg10` | Memory resource pressure. Average by 10 seconds |
| `cgroups_memory_pressure_full_avg300` | Memory resource pressure. Average by 300 seconds |
| `cgroups_memory_pressure_full_avg60` | Memory resource pressure. Average by 60 seconds |
| `cgroups_memory_pressure_full_total` | Memory resource pressure total |
| `cgroups_memory_pressure_some_avg10` | Memory resource pressure. Average by 10 seconds |
| `cgroups_memory_pressure_some_avg300` | Memory resource pressure. Average by 300 seconds |
| `cgroups_memory_pressure_some_avg60` | Memory resource pressure. Average by 60 seconds |
| `cgroups_memory_pressure_some_total` | Memory resource pressure total |
| `cgroups_memory_stat_active_anon` | memory statistic ('active_anon' field from 'memory.stat' file) |
| `cgroups_memory_stat_active_file` | memory statistic ('active_file' field from 'memory.stat' file) |
| `cgroups_memory_stat_cache` | memory statistic ('cache' field from 'memory.stat' file) |
| `cgroups_memory_stat_dirty` | memory statistic ('dirty' field from 'memory.stat' file) |
| `cgroups_memory_stat_hierarchical_memory_limit` | memory statistic ('hierarchical_memory_limit' field from 'memory.stat' file) |
| `cgroups_memory_stat_hierarchical_memsw_limit` | memory statistic ('hierarchical_memsw_limit' field from 'memory.stat' file) |
| `cgroups_memory_stat_inactive_anon` | memory statistic ('inactive_anon' field from 'memory.stat' file) |
| `cgroups_memory_stat_inactive_file` | memory statistic ('inactive_file' field from 'memory.stat' file) |
| `cgroups_memory_stat_mapped_file` | memory statistic ('mapped_file' field from 'memory.stat' file) |
| `cgroups_memory_stat_pgfault` | memory statistic ('pgfault' field from 'memory.stat' file) |
| `cgroups_memory_stat_pgmajfault` | memory statistic ('pgmajfault' field from 'memory.stat' file) |
| `cgroups_memory_stat_pgpgin` | memory statistic ('pgpgin' field from 'memory.stat' file) |
| `cgroups_memory_stat_pgpgout` | memory statistic ('pgpgout' field from 'memory.stat' file) |
| `cgroups_memory_stat_rss_huge` | memory statistic ('rss_huge' field from 'memory.stat' file) |
| `cgroups_memory_stat_rss` | memory statistic ('rss' field from 'memory.stat' file) |
| `cgroups_memory_stat_shmem` | memory statistic ('shmem' field from 'memory.stat' file) |
| `cgroups_memory_stat_swap` | memory statistic ('swap' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_active_anon` | memory statistic ('total_active_anon' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_active_file` | memory statistic ('total_active_file' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_cache` | memory statistic ('total_cache' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_dirty` | memory statistic ('total_dirty' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_inactive_anon` | memory statistic ('total_inactive_anon' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_inactive_file` | memory statistic ('total_inactive_file' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_mapped_file` | memory statistic ('total_mapped_file' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_pgfault` | memory statistic ('total_pgfault' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_pgmajfault` | memory statistic ('total_pgmajfault' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_pgpgin` | memory statistic ('total_pgpgin' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_pgpgout` | memory statistic ('total_pgpgout' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_rss_huge` | memory statistic ('total_rss_huge' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_rss` | memory statistic ('total_rss' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_shmem` | memory statistic ('total_shmem' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_swap` | memory statistic ('total_swap' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_unevictable` | memory statistic ('total_unevictable' field from 'memory.stat' file) |
| `cgroups_memory_stat_total_writeback` | memory statistic ('total_writeback' field from 'memory.stat' file) |
| `cgroups_memory_stat_unevictable` | memory statistic ('unevictable' field from 'memory.stat' file) |
| `cgroups_memory_stat_writeback` | memory statistic ('writeback' field from 'memory.stat' file) |
| `cgroups_memory_usage_kmem_max` | Maximum kernel memory usage |
| `cgroups_memory_usage_kmem_tcp` | Kernel TCP memory usage |
| `cgroups_memory_usage_kmem` | Maximum kernel TCP maximum memory usage |
| `cgroups_memory_usage_max` | Maximum memory usage |
| `cgroups_memory_usage_swap_max` | Maximum swap usage |
| `cgroups_memory_usage_swap` | Swap usage |
| `cgroups_memory_usage` | Memory usage |
| `cgroups_pids_count` | Process IDs count for this namespace |
| `cgroups_pids_max` | Maximum Process IDs allowed for this namespace |
| `cgroups_unified_stat_system_usec` | CPU statistic ('system_usec' field from 'cpu.stat' file) |
| `cgroups_unified_stat_usage_usec` | CPU statistic ('usage_usec' field from 'cpu.stat' file) |
| `cgroups_unified_stat_user_usec` | CPU statistic ('user_usec' field from 'cpu.stat' file) |
| `cgroups_unified_uptime` | init.scope uptime |
