from pygnmi.client import gNMIclient
from prettytable import PrettyTable
import yaml
import time
import logging

start = time.time()



def get_data(router, username, password, skip_verify=True):
    # Disable logging for the gNMIclient module
    logging.getLogger('pygnmi').setLevel(logging.CRITICAL)
    
    with gNMIclient(target=router, username=username, password=password, skip_verify=True) as gc:
         result = gc.get(path=['network-instance/protocols/bgp-evpn/bgp-instance'])
    
    # Enable logging for the gNMIclient module
    logging.getLogger('pygnmi').setLevel(logging.WARNING)

    return result


def create_table(router, network_instance):
    table = PrettyTable()
    table.field_names = ['Router', 'Network instance', 'ID', 'Admin state', 'Encapsulation type', 'VXLAN interface', 'EVI', 'ECMP', 'Oper state']
    table.align = 'l'
    table.add_row([router, network_instance['name'], '', '', '', '', '', '', ''])
    for bgp_instance in network_instance['protocols']['bgp-evpn']['srl_nokia-bgp-evpn:bgp-instance']:
        table.add_row(['', '', bgp_instance['id'], bgp_instance['admin-state'], bgp_instance['encapsulation-type'], bgp_instance['vxlan-interface'], bgp_instance['evi'], bgp_instance['ecmp'], bgp_instance['oper-state']])
    return str(table)




def main():
    with open('datacenter-nodes.yml', 'r') as fh:
        router_info = yaml.load(fh, Loader=yaml.SafeLoader)
    tmp01 = router_info['switches']
    routers = tmp01['srl']
    username = router_info['username']
    password = router_info['password']
    port = router_info['gnmi_port']
    skip_verify = router_info['skip_verify']
    for router in routers:
        # Get the data and extract the network instances
        result = get_data((router, port), username, password, skip_verify)
        for notification in result['notification']:
            for update in notification['update']:
                if 'srl_nokia-network-instance:network-instance' in update['val']:
                    network_instances = update['val']['srl_nokia-network-instance:network-instance']
                    for network_instance in network_instances:
                        table = create_table(router, network_instance)
                        print(table)
    end = time.time()
    float_format = '{0:.2F}'
    print(f'Total time: {float_format.format(end - start)} seconds')


if __name__ == "__main__":
    main()
