from pygnmi.client import gNMIclient
from prettytable import PrettyTable
import yaml
import time

start = time.time()

import logging

def get_data(router, username, password, skip_verify=True):
    # Disable logging for the gNMIclient module
    logging.getLogger('pygnmi').setLevel(logging.CRITICAL)
    
    with gNMIclient(target=router, username=username, password=password, skip_verify=skip_verify) as gc:
         result = gc.get(path=['network-instance/protocols/bgp-evpn/bgp-instance'])
    
    # Enable logging for the gNMIclient module
    logging.getLogger('pygnmi').setLevel(logging.WARNING)

    return result

def show_routers_table(routers):
    table = PrettyTable()
    table.field_names = ['Router']
    for router in routers:
        table.add_row([router])
    print(table)


def create_table(data, headers):
    table = PrettyTable()
    table.field_names = headers
    table.align = 'l'
    for row in data:
        table.add_row(row)
    return str(table)

def analyze_network_instance_evi(network_instance_name, network_instances):
    results = []
    for bgp_instance in network_instances[0]['protocols']['bgp-evpn']['srl_nokia-bgp-evpn:bgp-instance']:
        id = bgp_instance['id']
        evi_set = set()
        for network_instance in network_instances:
            bgp_instances = network_instance['protocols']['bgp-evpn']['srl_nokia-bgp-evpn:bgp-instance']
            for bgp_instance in bgp_instances:
                if bgp_instance['id'] == id:
                    evi_set.add(bgp_instance['evi'])
        if len(evi_set) == 1:
            evi = evi_set.pop()
            results.append([network_instance_name, f'ID {id} has EVI {evi} in all routers'])
        else:
            results.append([network_instance_name, f'ID {id} has different EVIs in the routers'])
    return results



def output_analysis_results(results):
    headers = ['Network instance', 'Analysis result']
    data = []
    for result in results:
        data.append(result)
    table = create_table(data, headers)
    print(table)

def main():
    with open('datacenter-nodes.yml', 'r') as fh:
        router_info = yaml.load(fh, Loader=yaml.SafeLoader)
    tmp01 = router_info['switches']
    routers = tmp01['srl']
    username = router_info['username']
    password = router_info['password']
    port = router_info['gnmi_port']
    skip_verify = router_info['skip_verify']
    network_instances = {}

    show_routers_table(routers)

    # Get the network instances for each router and add them to a dict
    for router in routers:
        result = get_data((router, port), username, password, skip_verify)
        for notification in result['notification']:
            for update in notification['update']:
                if 'srl_nokia-network-instance:network-instance' in update['val']:
                    for network_instance in update['val']['srl_nokia-network-instance:network-instance']:
                        if network_instance['name'] in network_instances:
                            network_instances[network_instance['name']].append(network_instance)
                        else:
                            network_instances[network_instance['name']] = [network_instance]

    # Analyze the network instances and output the results
    results = []
    for network_instance_name, instances in network_instances.items():
        results.extend(analyze_network_instance_evi(network_instance_name, instances))
    output_analysis_results(results)

    end = time.time()
    float_format = '{0:.2F}'
    print(f'Total time: {float_format.format(end - start)} seconds')    

if __name__ == "__main__":
    main()

