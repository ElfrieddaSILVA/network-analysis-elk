from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel

from utils.net import containernet_handler



def topo(topofilename='topo.out', measfilename='meas.out', **kwargs):
    with containernet_handler(controller=Controller) as net:

        info('*** Ajout du contrôleur\n')
    
        net.addController('c0')
    
        info('*** Ajout des conteneurs Docker\n')

        srv_limits = {
            'cpu_quota':        -1,
            'cpu_period':       None,
            'cpu_shares':       None,
            'mem_limit':        None,
            'memswap_limit':    None,
        }
        srv_limits = kwargs.get('limits') or srv_limits
        
       


        nginx = net.addDocker('nginx',
                            ip='10.0.0.251',
                            dimage="nginx-open-srv:latest",
                            ports=[80],
                            environment={
                                'SRV_PORT': '5000',
                                'LISTEN_PORT': '80',
                            },
                            **srv_limits
                            )

           

        nginx_lb = net.addDocker('nginx_lb',
                            ip='10.0.0.252',
                            dimage="nginx-open-lb:latest",
                            ports=[80],
                            environment={
                                'SERVER1_IP': '10.0.0.10',
                                'SERVER1_PORT': '5000',
                                'SERVER2_IP': '10.0.0.11',
                                'SERVER2_PORT': '5000',
                                'LISTEN_PORT': '80',
                            } 
                            )

        wrk = net.addDocker('wrk',
                            ip='10.0.0.253',
                            dimage="wrk2:latest")
           
        servers_kwargs = {
            'srv1': {
                'ip': '10.0.0.10',
                'dimage': 'flask:latest',
                'ports': [5000],
                'environment': {'SRVNAME': 'srv1'}
                },
            'srv2': {
                'ip': '10.0.0.11',
                'dimage': 'flask:latest',
                'ports': [5000],
                'environment': {'SRVNAME': 'srv2'}
                },
            }
    
        servers = {}
    
    
        for key in servers_kwargs:
            servers[key] = net.addDocker(key, **servers_kwargs[key])
    
    
        info('*** Ajout des switchs\n')
        
        s1 = net.addSwitch('s1')
        s2 = net.addSwitch('s2')
        s3 = net.addSwitch('s3')
        s4 = net.addSwitch('s4')
        s5 = net.addSwitch('s5')

    
        info('*** Création des connexions\n')
        
        
        net.addLink(s1, s2, cls=TCLink, delay='100ms', bw=1)
        net.addLink(wrk, s2)
        net.addLink(s2, s3, cls=TCLink, delay='50ms', bw=1)
        net.addLink(s2, s4)
        net.addLink(s3, nginx)
        net.addLink(s4, nginx_lb)
        net.addLink(s4, s5)
        
        
    
        for srv in servers.values():
            net.addLink(s5, srv)
        
        info('*** Démarrage du réseau\n')
        
        net.start()
        
    
        info('*** Configuration de la couche 4\n')
    
        nginx_lb.cmd("envsubst < /root/lb-config/simple_lb.conf > /root/lb-config/default.conf && nginx -c /root/lb-config/default.conf")

        nginx.cmd("envsubst < /root/nginx-conf/open.conf > /root/nginx-conf/default.conf && nginx -c /root/nginx-conf/default.conf")
        nginx.cmd("FLASK_APP=/root/matrix-srv/main.py flask run &")

        for srv in servers.values():
            srv.cmd("bash -c 'python3 -m flask run --host=0.0.0.0 2> /dev/null > /dev/null &'")
    
    
        info('*** Démarrage des tests\n')

        commands = [
            'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80',
             'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.252:80',
        ]
        commands = kwargs.get('commands') or commands

        results = []

        for comm in commands:
            print(f'En cours: {comm}')
            results.append(wrk.cmd(comm))


        info('*** Sauvegarde des résultats\n')

        
        with open(measfilename, 'w+') as f:
            f.write(str(srv_limits))
            f.write('\n')
            f.write('\n')
            for i in range(len(commands)):
                f.write(commands[i])
                f.write('\n')
                f.write('\n')
                f.write(results[i])
                f.write('\n')


        with open(topofilename, 'w+') as f:
            for _, item in net.items():
                item_repr = repr(item)
                item_repr = item_repr.replace('<Docker ', '<Host ')
                f.write(item_repr)
                f.write('\n')

            f.write('\n')
            f.write('===' * 20)
            f.write('\n')
            
            for link in net.links:
                f.write(str(link))
                f.write('\n')

