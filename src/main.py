import time
import argparse
import re
import json
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel

from utils.net import containernet_handler

setLogLevel('info')

def green(msg):
  print("\033[92m{}\033[0m".format(msg))

def parse_wrk_output(data):
    print("Parsing the wrk output")
    # Regular expressions to extract relevant data
    latency_pattern = r"Latency\s+(\S+)\s+(\S+)\s+(\S+)\s+([0-9.]+)%"
    req_sec_pattern = r'Req/Sec\s+(\S+)\s+(\S+)\s+(\S+)\s+([0-9.]+)%'
    latency_distr_50 = r"50.000%\s+(.+)\s"
    latency_distr_75 = r"75.000%\s+(.+)\s"
    latency_distr_90 = r"90.000%\s+(.+)\s"
    latency_distr_99 = r"99.000%\s+(.+)\s"
    latency_distr_99_900 = r"99.900%\s+(.+)\s"
    latency_distr_99_990 = r"99.990%\s+(.+)\s"
    latency_distr_99_999 = r"99.999%\s+(.+)\s"
    latency_distr_100 = r"100.000%\s+(.+)\s"

    # Extracting latency data
    latency_matches = re.search(latency_pattern, data)
    latency_50_matches = re.search(latency_distr_50, data)
    latency_75_matches = re.search(latency_distr_75, data)
    latency_90_matches = re.search(latency_distr_90, data)
    latency_99_matches = re.search(latency_distr_99, data)
    latency_99_900_matches = re.search(latency_distr_99_900, data)
    latency_99_990_matches = re.search(latency_distr_99_990, data)
    latency_99_999_matches = re.search(latency_distr_99_999, data)
    latency_100_matches = re.search(latency_distr_100, data)

    latency_avg = float(latency_matches.group(1).rstrip('s'))
    latency_stdev = float(latency_matches.group(2).rstrip('s'))
    latency_max = float(latency_matches.group(3).rstrip('s'))

    latency_50 = latency_50_matches.group(1)
    latency_50 = float(latency_50.replace('s', ''))
    latency_75 = latency_75_matches.group(1)
    latency_75 = float(latency_75_matches.group(1).replace('s', ''))
    latency_90 = latency_90_matches.group(1)
    latency_90 = float(latency_90_matches.group(1).replace('s', ''))
    latency_99 = latency_99_matches.group(1)
    latency_99 = float(latency_99_matches.group(1).replace('s', ''))
    latency_99_900 = latency_99_900_matches.group(1)
    latency_99_900 = float(latency_99_900_matches.group(1).replace('s', ''))
    latency_99_990 = latency_99_900_matches.group(1)
    latency_99_990 = float(latency_99_990_matches.group(1).replace('s', ''))
    latency_99_999 = latency_99_999_matches.group(1)
    latency_99_999 = float(latency_99_999_matches.group(1).replace('s', ''))
    latency_100 = latency_100_matches.group(1)
    latency_100 = float(latency_100_matches.group(1).replace('s', ''))

    # Extracting Req/Sec data
    req_sec_matches = re.search(req_sec_pattern, data)
    req_sec_avg = req_sec_matches.group(1)
    req_sec_stdev = req_sec_matches.group(2)
    req_sec_max = req_sec_matches.group(3)
    req_sec_percentage = req_sec_matches.group(4)


    

    # Creating a JSON object
    return {
        "latency_avg": float(latency_avg),
        "latency_stdev": float(latency_stdev),
        "latency_max": float(latency_max),
        "req_per_sec_avg": float(req_sec_avg),
        "req_per_sec_stdev": float(req_sec_stdev),
        "req_per_sec_max": float(req_sec_max),
        "req_per_second_percentage": float(req_sec_percentage),
        "latency_50": latency_50,
        "latency_75": latency_75,
        "latency_90": latency_90,
        "latency_99": latency_99,
        "latency_99_900": latency_99_900,
        "latency_99_990": latency_99_990,
        "latency_99_999": latency_99_999,
        "latency_100": latency_100,
    }

    # # Convert to JSON format
    # json_result = json.dumps(result, indent=4)

    # # Print the JSON data
    # print(json_result)
            

def parse_sysbench_output(output):
  
  transactions_per_second_regex = r"transactions:\s+\d+\s+\((.+) per sec\.\)"
  transactions_per_second = re.search(transactions_per_second_regex, output).group(1)

  queries_per_second_regex = r"queries:\s+\d+\s+\((.+) per sec\.\)"
  queries_per_second = re.search(queries_per_second_regex, output).group(1)

  latency_regex = r"Latency \(ms\):\s+min:\s+(.+)\s+avg:\s+(.+)\s+max:\s+(.+)\s+95th percentile:\s+(.+)"
  latency_min, latency_avg, latency_max, latency_95th = re.search(latency_regex, output).groups()

  return {
    'transactions_per_second': float(transactions_per_second),
    'queries_per_second': float(queries_per_second),
    'latency_min': float(latency_min),
    'latency_avg': float(latency_avg),
    'latency_max': float(latency_max),
    'latency_95th': float(latency_95th),
  }


def remove_ansi_escape_sequences(s: str) -> str:
  return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', s)


def execute_sql(container, sql: str) -> str:
  output = container.cmd(f"PGPASSWORD=postgres psql -U postgres -A -t -X -c \"{sql}\"")
  return remove_ansi_escape_sequences(output).strip();

def topo(topofilename='topo.out', measfilename='meas.out', sysbench_out ='sysbench.jsonl', **kwargs):
    with containernet_handler(controller=Controller) as net:

        green('*** Ajout du contrôleur\n')
    
        net.addController('c0')
    
        green('*** Ajout des conteneurs Docker\n')

        srv_limits = {
            'cpu_quota':        -1,
            'cpu_period':       None,
            'cpu_shares':       None,
            'mem_limit':        None,
            'memswap_limit':    None,
        }
        srv_limits = kwargs.get('limits') or srv_limits
        
        db_limits = {
            'replicas': 1,
            'delay': 0,
            'loss': 0,
            'primary_cpu': 0.5,
            'replica_cpu': 0.5,
            'primary_memory': 1000,
            'primary_swap_memory': 1000,
            'replica_memory': 1000,
            'replica_swap_memory': 1000,
        }

        db_limits = kwargs.get('db_limits') or db_limits

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
    
       
        primary = net.addDocker(
            'primary',
            ip='10.1.0.100',
            dcmd="/opt/bitnami/scripts/postgresql/entrypoint.sh /opt/bitnami/scripts/postgresql/run.sh",
            dimage="tip-postgres:latest",
            cpu_period=100000,
            cpu_quota=int(db_limits['primary_cpu'] * 100000),
            mem_limit=int(db_limits['primary_memory']) * 1024 * 1024,
            memswap_limit=int(db_limits['primary_swap_memory']) * 1024 * 1024,
            port_bindings={5432: 5432},
            environment={
                "POSTGRESQL_REPLICATION_MODE": "master",
                "POSTGRESQL_REPLICATION_USER": "postgres",
                "POSTGRESQL_REPLICATION_PASSWORD": "postgres",
                "POSTGRESQL_USERNAME": "postgres",
                "POSTGRESQL_PASSWORD": "postgres",
                "POSTGRESQL_DATABASE": "postgres",
                "POSTGRESQL_SYNCHRONOUS_COMMIT_MODE": "remote_apply",
                "POSTGRESQL_NUM_SYNCHRONOUS_REPLICAS": db_limits['replicas'],
                "ALLOW_EMPTY_PASSWORD": "yes"
            },
        )

        replicas = []
        for i in range(db_limits['replicas']):
            green(f'Démarrage de la réplique {i}')
            replicas.append(net.addDocker(
                'replica' + str(i),
                ip='10.1.0.' + str(200 + i),
                dcmd="/opt/bitnami/scripts/postgresql/entrypoint.sh /opt/bitnami/scripts/postgresql/run.sh",
                dimage="tip-postgres:latest",
                cpu_period=100000,
                cpu_quota=int(db_limits['replica_cpu'] * 100000),
                mem_limit=int(db_limits['replica_memory']) * 1024 * 1024,
                memswap_limit=int(db_limits['replica_swap_memory']) * 1024 * 1024,
                port_bindings={5432: 5433 + i},
                environment={
                    "POSTGRESQL_REPLICATION_MODE": "slave",
                    "POSTGRESQL_REPLICATION_USER": "postgres",
                    "POSTGRESQL_REPLICATION_PASSWORD": "postgres",
                    "POSTGRESQL_MASTER_HOST": "10.1.0.100",
                    "POSTGRESQL_PASSWORD": "postgres",
                    "POSTGRESQL_MASTER_PORT_NUMBER": "5432",
                    "ALLOW_EMPTY_PASSWORD": "yes",
                },
            ))


        green('Démarrage du conteneur de benchmark PostgreSQL')
        benchmark = net.addDocker(
            'benchmark',
            ip='10.1.0.250',
            dimage="sysbench:latest",
            cpu_period=100000,
            cpu_quota=100000,
        )

        green('*** Ajout des switchs\n')
        s1 = net.addSwitch('s1', cls=OVSSwitch)
        s2 = net.addSwitch('s2', cls=OVSSwitch)
        s3 = net.addSwitch('s3', cls=OVSSwitch)
        s4 = net.addSwitch('s4', cls=OVSSwitch)
        s5 = net.addSwitch('s5', cls=OVSSwitch)

        
        green('*** Création des connexions\n')
        net.addLink(primary, s1)

        for replica in replicas:
          net.addLink(replica, s1, cls=TCLink, bw=100, delay=f"{db_limits['delay']}ms", loss=db_limits['loss'])

        net.addLink(benchmark, s1)
        net.addLink(s1, s2, cls=TCLink, delay='100ms', bw=1)
        net.addLink(wrk, s2)
        net.addLink(s2, s3, cls=TCLink, delay='50ms', bw=1)
        net.addLink(s2, s4, cls=TCLink, delay='100ms', bw=1)
        net.addLink(s3, nginx)
        net.addLink(s4, nginx_lb)
        net.addLink(s4, s5, cls=TCLink, delay='100ms', bw=1)
        

        for srv in servers.values():
            net.addLink(s5, srv)
            
        green('*** Démarrage du réseau\n')
        
        net.start()
            
        
        green('*** Configuration de la couche 4\n')

        nginx_lb.cmd("envsubst < /root/lb-config/simple_lb.conf > /root/lb-config/default.conf && nginx -c /root/lb-config/default.conf")

        nginx.cmd("envsubst < /root/nginx-conf/open.conf > /root/nginx-conf/default.conf && nginx -c /root/nginx-conf/default.conf")
        nginx.cmd("FLASK_APP=/root/matrix-srv/main.py flask run &")

        for srv in servers.values():
            srv.cmd("bash -c 'python3 -m flask run --host=0.0.0.0 2> /dev/null > /dev/null &'")
        
        green('En attente du démarrage de toutes les répliques')
        for _ in range(20):
            replica_count = execute_sql(primary, "select count(*) from pg_stat_replication where application_name = 'walreceiver' and sync_state = 'sync';")
            print("Répliques prêtes: ", replica_count)

            if replica_count == str(db_limits['replicas']):
                break
            else:
                time.sleep(4)

        green('====> Préparation du benchmark de PostgreSQL')
        benchmark.cmd("sysbench --db-driver=pgsql --pgsql-host=10.1.0.100 --pgsql-user=postgres --pgsql-password=postgres --pgsql-db=postgres oltp_read_write prepare")

        green('*** Démarrage des tests\n')

        green('**** Démarrage du benchmark de PostgreSQL')
        start = time.time()
        benchmark_output = benchmark.cmd("sysbench --db-driver=pgsql --pgsql-host=10.1.0.100 --pgsql-user=postgres --pgsql-password=postgres --pgsql-db=postgres oltp_read_write run")
        end = time.time()

        green('Sauvegarde des résultats du benchmark de Postgres')
        benchmark_results = parse_sysbench_output(benchmark_output)

        run_data = {
            'replicas': db_limits['replicas'],
            'delay': db_limits['delay'],
            'loss': db_limits['loss'],
            'time': end - start,
            'primary_cpu': db_limits['primary_cpu'],
            'replica_cpu': db_limits['replica_cpu'],
            'primary_memory': db_limits['primary_memory'],
            'primary_swap_memory': db_limits['primary_swap_memory'],
            'replica_memory': db_limits['replica_memory'],
            'replica_swap_memory': db_limits['replica_swap_memory'],
        }

        print("Enregistrement des résultats du benchmark de PostgreSQL dans le fichier: " + sysbench_out)
        with open(sysbench_out, "a") as outfile:
            outfile.write(json.dumps({**run_data, **benchmark_results}) + "\n")

        green('**** Démarrage du benchmark WRK')

        commands = [
            'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.251:80',
            'wrk -t2 -c100 -d30s -R2000 --latency http://10.0.0.252:80',
        ]
        commands = kwargs.get('commands') or commands

        results = []

        for comm in commands:
            print(f'En cours: {comm}')
            results.append(wrk.cmd(comm))


        green('*** Sauvegarde des résultats du benchmark nginx\n')   
        print("Enregistrement dans le fichier %s" %measfilename)     
        with open(measfilename, 'w+') as f:
            for i in range(len(commands)):
                f.write(json.dumps({**srv_limits, **parse_wrk_output(results[i])}) + "\n")
        #     f.write(str(srv_limits))
        #     f.write('\n')
        #     f.write('\n')
        #     for i in range(len(commands)):
        #         f.write(commands[i])
        #         f.write('\n')
        #         f.write('\n')
        #         f.write(results[i])
        #         f.write('\n')

        # with open(measfilename, "w+") as f:
        #     #f.write(json.dumps(str(srv_limits)))
        #     for i in range(len(commands)):
        #         json.dumps(parse_wrk_output(results[i]), f)
                # f.write(
                #     str(parse_wrk_output(results[i]))
                # )


        print("Enregistrement dans le fichier %s" %topofilename)   
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

