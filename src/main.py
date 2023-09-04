from mininet.log import info, setLogLevel

import topos.clitest as test
import topos.simple_lb as simple
import topos.single_webserver as single_webserver
import topos.full_architecture as load_balancer
import topos.cluster as cluster

import os

setLogLevel('info')



def cluster_meas():
    commands = [
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/mmul/15',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/lu/15',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/qr/15',
    ]

    if not os.path.isdir('results'):
        os.mkdir('results')

    # Cluster

    cpu_period = 100000
    limits = {
        'cpu_quotas': int( 1.0 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': '1024m',
        'memswap_limit': None,
    }
    cluster.topo(
        topofilename='results/topo.out',
        measfilename='results/klast-meas-1.out',
        weights=[1,1],
        commands=commands,
        limits=limits
        )


    limits = {
        'cpu_quotas': int( 2.0 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': '1024m',
        'memswap_limit': None,
    }
    cluster.topo(
        measfilename='results/klast-meas-2.out',
        weights=[1,1],
        commands=commands,
        limits=limits
        )


    limits = {
        'cpu_quotas': int( 3.0 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': '1024m',
        'memswap_limit': None,
    }
    cluster.topo(
        measfilename='results/klast-meas-3.out',
        weights=[1,1],
        commands=commands,
        limits=limits
        )


    # Single

    limits = {
        'cpu_quotas': int( 1.0 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': '1024m',
        'memswap_limit': None,
    }
    cluster.topo(
        measfilename='results/singl-meas-1.out',
        weights=[1,0],
        commands=commands,
        limits=limits
        )


    limits = {
        'cpu_quotas': int( 2.0 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': '1024m',
        'memswap_limit': None,
    }
    cluster.topo(
        measfilename='results/singl-meas-2.out',
        weights=[1,0],
        commands=commands,
        limits=limits
        )


    limits = {
        'cpu_quotas': int( 3.0 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': '1024m',
        'memswap_limit': None,
    }
    cluster.topo(
        measfilename='results/singl-meas-3.out',
        weights=[1,0],
        commands=commands,
        limits=limits
        )

def webserver_test():
    commands = [
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/mmul/10',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/mmul/20',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/mmul/30',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/lu/10',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/lu/20',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/lu/30',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/qr/10',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/qr/20',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/qr/30',
    ]

    cpu_period = 100000
    limits = {
        'cpu_quotas': int( 1.0 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': None,
        'memswap_limit': None,
    }
    

    # No limits
    single_webserver.topo(
        topofilename='results/topo-full.out',
        measfilename='results/meas-full.out',
        commands=commands,
        limits=limits
    )


    limits = {
        'cpu_quotas': int( 0.5 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': None,
        'memswap_limit': None,
    }

    # Half of cpu
    single_webserver.topo(
        topofilename='results/topo-half.out',
        measfilename='results/meas-half.out',
        commands=commands,
        limits=limits
    )


    limits = {
        'cpu_quotas': int( 0.25 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': None,
        'memswap_limit': None,
    }

    # Quater of cpu
    single_webserver.topo(
        topofilename='results/topo-quarter.out',
        measfilename='results/meas-quarter.out',
        commands=commands,
        limits=limits
    )


    limits = {
        'cpu_quotas': int( 0.25 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': '32m',
        'memswap_limit': -1,
    }

    # Memory 12m
    single_webserver.topo(
        topofilename='results/topo-quarter-mem32.out',
        measfilename='results/meas-quarter-mem32.out',
        commands=commands,
        limits=limits
    )


    limits = {
        'cpu_quotas': int( 0.25 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': '16m',
        'memswap_limit': -1,
    }

    # Memory 6m
    single_webserver.topo(
        topofilename='results/topo-quarter-mem16.out',
        measfilename='results/meas-quarter-mem16.out',
        commands=commands,
        limits=limits
    )

def load_balancer_test():
    commands = [
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/mmul/10',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/mmul/20',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80/mmul/30',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.252:80/mmul/10',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.252:80/mmul/20',
        'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.252:80/mmul/30',
    ]

    cpu_period = 100000
    limits = {
        'cpu_quotas': int( 1.0 * cpu_period ),
        'cpu_period': cpu_period,
        'cpu_shares': None,
        'mem_limit': None,
        'memswap_limit': None,
    }

    db_limits = {
        'replicas': 4,
        'delay': 0,
        'loss': 0,
        'primary_cpu': 1,
        'replica_cpu': 0.5,
        'primary_memory': 1000,
        'primary_swap_memory': 1000,
        'replica_memory': 1000,
        'replica_swap_memory': 1000,
    }
    # No limits
    load_balancer.topo(
        topofilename='/full_arch_topo.out',
        measfilename='/full_arch_meas.jsonl',
        commands=commands,
        sysbench_out='/full_arch_sysbench.jsonl',
        limits=limits,
        db_limits=db_limits,
    )



def main():
#    test.topo()
#simple.topo()
    load_balancer_test()
#   webserver_test()
#  cluster_meas()


if __name__ == '__main__':
    main()

