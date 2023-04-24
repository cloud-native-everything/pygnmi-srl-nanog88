from pygnmi.client import gNMIclient
import yaml
import logging

def create_tunnel_interface(router, username, password, skip_verify=True):
    # Disable logging for the gNMIclient module
    logging.getLogger('pygnmi').setLevel(logging.CRITICAL)
    
    with gNMIclient(target=router, username=username, password=password, skip_verify=True, gnmi_timeout=10) as gc:
        # Define the path for the tunnel interface
        path = f'tunnel-interface[name=vxlan100]'
        
        # Set the config for the tunnel interface
        tunnel_config = {
            'name': 'vxlan100',
            'description': 'VXLAN tunnel interface',
            'admin-state': 'enable'
        }
        

        update = [{'path': path, 'val': tunnel_config}]
        print(update)
        gc.set(update, timeout=10)

    # Enable logging for the gNMIclient module
    logging.getLogger('pygnmi').setLevel(logging.WARNING)

def main():
    with open('datacenter-nodes-ips.yml', 'r') as fh:
        router_info = yaml.load(fh, Loader=yaml.SafeLoader)
    
    tmp01 = router_info['switches']
    routers = tmp01['srl']
    username = router_info['username']
    password = router_info['password']
    skip_verify = router_info['skip_verify']
    
    
    for router in routers:
        print(router)
        create_tunnel_interface(router, username, password, skip_verify)
        print(f"Tunnel interface created on {router} with VXLAN interfaces")

if __name__ == "__main__":
    main()

