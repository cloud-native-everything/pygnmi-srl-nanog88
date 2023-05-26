from pygnmi.client import gNMIclient
from prettytable import PrettyTable
import yaml
import time
import logging

start = time.time()

class BgpEvpn:
    def __init__(self, network_instance, id, admin_state, vxlan_interface, evi, ecmp, oper_state):
        self.network_instance = network_instance
        self.id = id
        self.admin_state = admin_state
        self.vxlan_interface = vxlan_interface
        self.evi = evi
        self.ecmp = ecmp
        self.oper_state = oper_state

class BgpVpn:
    def __init__(self, network_instance, id, rd, export_rt, import_rt):
        self.network_instance = network_instance
        self.id = id
        self.rd = rd
        self.export_rt = export_rt
        self.import_rt = import_rt        

class SrlDevice:
    def __init__(self, router, port, model, release, username, password, skip_verify=True):
        self.router = router
        self.port = port
        self.password = password
        self.useername = username
        self.skip_verify = skip_verify
        self.model = model
        self.release = release
        self.bgp_evpn = []
        self.bgp_vpn = []

    def get_bgp_evpn_info(self):
        # Disable logging for the gNMIclient module
        logging.getLogger('pygnmi').setLevel(logging.CRITICAL)
        
        with gNMIclient(target=self.router, username=self.username, password=self.password, skip_verify=self.skip_verify) as gc:
            result = gc.get(path=['network-instance/protocols/bgp-evpn/bgp-instance'])
        
        # Enable logging for the gNMIclient module
        logging.getLogger('pygnmi').setLevel(logging.WARNING)
        for notification in result['notification']:
                    for update in notification['update']:
                        if 'srl_nokia-network-instance:network-instance' in update['val']:
                            network_instances = update['val']['srl_nokia-network-instance:network-instance']             
                            for network_instance in network_instances:
                                for bgp_instance in network_instance['protocols']['bgp-evpn']['srl_nokia-bgp-evpn:bgp-instance']:
                                    if not('oper-state' in bgp_instance):
                                        self.bgp_evpn.append(BgpEvpn(self.router, network_instance['name'], bgp_instance['id'], bgp_instance['admin-state'], bgp_instance['vxlan-interface'], bgp_instance['evi'], bgp_instance['ecmp'], "waiting"))    
                                    else:   
                                        self.bgp_evpn.append(BgpEvpn(self.router, network_instance['name'], bgp_instance['id'], bgp_instance['admin-state'], bgp_instance['vxlan-interface'], bgp_instance['evi'], bgp_instance['ecmp'], bgp_instance['oper-state']))

    def get_bgp_vpn_info(self):
        # Disable logging for the gNMIclient module
        logging.getLogger('pygnmi').setLevel(logging.CRITICAL)
        
        with gNMIclient(target=self.router, username=self.username, password=self.password, skip_verify=self.skip_verify) as gc:
            result = gc.get(path=['network-instance/protocols/bgp-evpn/bgp-instance'])
        
        # Enable logging for the gNMIclient module
        logging.getLogger('pygnmi').setLevel(logging.WARNING)
        for notification in result['notification']:
                    for update in notification['update']:
                        if 'srl_nokia-network-instance:network-instance' in update['val']:
                            network_instances = update['val']['srl_nokia-network-instance:network-instance']             
                            for network_instance in network_instances:
                                for bgp_instance in network_instance['protocols']['bgp-evpn']['srl_nokia-bgp-evpn:bgp-instance']:
                                        self.bgp_vpn.append(BgpVpn(self.router, network_instance['name'], bgp_instance['id'], bgp_instance['route-distinguisher']['rd'], bgp_instance['route-target']['export-rt'],bgp_instance['route-target']['import-rt']))    


    def connect(self):
        print(f"Connecting to device: {self.name} with IP: {self.ip}")

    def configure(self, configuration):
        print(f"Applying configuration to {self.name}: \n{configuration}")

def main():
    with open('datacenter-nodes.yml', 'r') as fh:
        router_info = yaml.load(fh, Loader=yaml.SafeLoader)
    tmp01 = router_info['switches']
    routers = tmp01['srl']
    username = router_info['username']
    password = router_info['password']
    port = router_info['gnmi_port']
    skip_verify = router_info['skip_verify']
    table = PrettyTable()
    table.field_names = ['Router', 'Network instance', 'ID', 'Admin state', 'VXLAN interface', 'EVI', 'ECMP', 'Oper state'] 
    table.align = 'l'
    srl_devices = []
    for router in routers:
        srl_devices.append(SrlDevice(router, port, 'ixrd3', '21.6.4', username, password, skip_verify))

    table = PrettyTable()
    table.field_names = ['Router', 'Network instance', 'ID', 'Admin state', 'VXLAN interface', 'EVI', 'ECMP', 'Oper state', 'RD', 'import-rt', 'export-rt'] 
    table.align = 'l'        
    for device in srl_devices:
        device.get_bgp_evpn_info
        device.get_bgp_vpn_info    
        for evpn_inst in device.bgp_evpn:
             table.add_row([device.router, evpn_inst.network_instance, evpn_inst.id , evpn_inst.admin_state, evpn_inst.vxlan_interface, evpn_inst.evi, evpn_inst.ecmp, evpn_inst.oper_state])  
        
    print(table)

if __name__ == '__main__':
    main()
    end = time.time()
    float_format = '{0:.2F}'
    print(f'Total time: {float_format.format(end - start)} seconds')