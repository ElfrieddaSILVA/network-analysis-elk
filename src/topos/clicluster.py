from mininet.node import Controller
from mininet.link import TCLink
from mininet.log import info, setLogLevel

from utils.net import containernet_handler




def topo(topofilename='topo.out', measfilename='meas.out', **kwargs):

    with containernet_handler(controller=Controller) as net:

        info('*** Adding controller\n')
    
        net.addController('c0')
    
        info('*** Adding docker containers\n')


        srv_limits = {
            'cpu_quota':        -1,
            'cpu_period':       None,
            'cpu_shares':       None,
            'mem_limit':        None,
            'memswap_limit':    None,
        }
        srv_limits = kwargs.get('limits') or srv_limits
        

        # Master
        master_name = 'nginx1'
        master_ip = '10.0.0.250'
        worker_name = 'nginx2'
        worker_ip = '10.0.0.251'
        vip1 = '10.0.0.213'
        vip2 = '10.0.0.217'

        nginx1 = net.addDocker(master_name,
                            ip=master_ip,
                            dimage="nginx-plus-srv:latest",
                            ports=[80, 2000],
                            environment={
                                'PRIORITY':         '101',
                                'INTERFACE_NAME':   master_name + '-eth0',
                                'SRC_IP':           master_ip,
                                'PEER_IP':          worker_ip,
                                'VIP_1':            vip1,
                                'VIP_2':            vip2,
                                'PRIORITY_2':       '99',
                            },
                            **srv_limits
                            )

        # Worker
        nginx2 = net.addDocker(worker_name,
                            ip=worker_ip,
                            dimage="nginx-plus-srv:latest",
                            ports=[80, 2000],
                            environment={
                                'PRIORITY':         '100',
                                'INTERFACE_NAME':   worker_name + '-eth0',
                                'SRC_IP':           worker_ip,
                                'PEER_IP':          master_ip,
                                'VIP_1':            vip1,
                                'VIP_2':            vip2,
                                'PRIORITY_2':       '100',
                            },
                            **srv_limits
                            )


        #
        # Weights are described in nginx docs.
        # If weight is zero upstream is set to backup.
        #

        weights = kwargs.get('weights', [1, 1])
        lb_weights_params = []
        
        for weight in weights:
            if weight > 0:
                lb_weights_params.append(f'weight={weight}')
            elif weight == 0:
                lb_weights_params.append('backup')
            else:
                lb_weights_params.append('')


        nginxlb = net.addDocker('lb',
                            ip='10.0.0.25',
                            dimage="nginx-plus-lb:latest",
                            ports=[80],
                            environment={
                                'SERVER1_IP': vip1,
                                'SERVER1_PORT': '80',
                                'UPSTREAM_SRV_PARAMS_1': lb_weights_params[0],
                                'SERVER2_IP': vip2,
                                'SERVER2_PORT': '80',
                                'UPSTREAM_SRV_PARAMS_2': lb_weights_params[1],
                                'LISTEN_PORT': '80',
                            } 
                            )


        wrk = net.addDocker('wrk',
                            ip='10.0.0.252',
                            dimage="wrk2:latest")
           
    
        info('*** Adding switches\n')
        
        s1 = net.addSwitch('s1')
    
        info('*** Creating links\n')
        
        net.addLink(wrk, s1)
        net.addLink(s1, nginx1)
        net.addLink(s1, nginx2)
        net.addLink(s1, nginxlb)


        info('*** Starting network\n')
        
        net.start()
        
    
        info('*** Setuping layer 4\n')


        nginxlb.cmd("envsubst < /root/lb-config/simple_lb.conf > /root/lb-config/default.conf && nginx -c /root/lb-config/default.conf")


        cluster_containers = [
            nginx1, 
            nginx2,
        ]
       
        for cont in cluster_containers:
            cont.cmd("envsubst < /root/nginx-conf/plus.conf.d/keepalived.conf > /etc/keepalived/keepalived.conf")
            cont.cmd("/root/nginx-conf/plus.conf.d/configure.sh")
            cont.cmd("FLASK_APP=/root/matrix-srv/main.py flask run &")
            cont.cmd("keepalived")

        from mininet.cli import CLI
        CLI(net)
