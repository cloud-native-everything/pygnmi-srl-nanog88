import pygnmi.client as gc

srl_address = 'clab-dc-k8s-LEAF-DC-2'
srl_port = 57400
srl_username = 'admin'
srl_password = 'admin'

# Define the GNMI path to the routing table
routing_table_path = {
    'elem': [
        {'name': 'network-instances'},
        {'name': 'network-instance', 'key': {'name': 'default'}},
        {'name': 'routing'},
        {'name': 'ipv4'},
        {'name': 'unicast'}
    ]
}

# Connect to SRL using GNMI
with gc.gNMIclient(target=(srl_address, srl_port), username=srl_username, password=srl_password) as c:
    # Get the route table
    result = c.get(routing_table_path)

# Print the route table
print(result)
