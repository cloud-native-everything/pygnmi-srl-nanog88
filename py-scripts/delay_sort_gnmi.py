from pygnmi.client import gNMIclient
from pysros.pprint import Table, Padding
from collections import defaultdict
import sys, yaml, time

start = time.time()

DELAY_DB = defaultdict()
ROWS_DB = defaultdict()

def get_data(router, username, password, insecure=True):
    with gNMIclient(target=router, username=username, password=password, insecure=True) as gc:
         result = gc.get(path=['/nokia-state:state/router/interface/if-attribute/delay'])
    return result


def check_delay(router, results, delay_db):
    delay_list = results['notification'][0]['update']
    if_db = defaultdict()
    for item in delay_list:
        if_name = item['path'][56:][:-20]
        if_delay = item['val']['operational']
        if_db[if_name] = if_delay
    delay_db[router] = if_db


def create_table_rows(delay_db, rows_db):
    for rtr in delay_db.keys():
        for if_name in delay_db[rtr].keys():
            oper_delay = delay_db[rtr][if_name]
            other_rtr = if_name.split('_')[1]
            other_if_name = 'to_' + rtr
            if other_rtr in delay_db.keys():
                other_oper_delay = delay_db[other_rtr][other_if_name]
                newkey = create_key(rtr, other_rtr)
            else:
                other_oper_delay = "N/A"
                newkey = rtr + '_and_NONE'
            rows_db[newkey] = [ rtr, if_name, oper_delay, "<-->", other_oper_delay, other_if_name, other_rtr ]


def create_key(r1, r2):
    if r1[1:] < r2[1:]:
        key = r1 + '_and_' + r2
    else:
        key = r2 + '_and_' + r1
    return key


def print_table(rows_db):
    rows = []
    for k, row in rows_db.items():
        rows.append(row)
    summary = '''Combined report for delay on all interfaces for routers
defined in router_info.yml'''
    if_col_hdr = [(6, 'Router', '<'), (9, 'Interface', '<'), (6, 'Delay', '^'), (8, '', '^'), (6, 'Delay', '^'), (9, 'Interface', '>'), (6, 'Router', '>')]
    tbl_width = sum([col[0] for col in if_col_hdr]) + len(if_col_hdr)
    delay_table = Table('Interface delay measurements',
                        columns = if_col_hdr,
                        summary = summary,
                        showCount = None,
                        width = tbl_width)
    delay_table.print(rows)


def main():
    with open('router_info.yml', 'r') as fh:
        router_info = yaml.load(fh, Loader=yaml.SafeLoader)
    tmp01 = router_info['routers']
    routers = tmp01['sros']
    username = router_info['username']
    password = router_info['password']
    port = router_info['gnmi_port']
    insecure = router_info['insecure']
    for router in routers:
        results = get_data((router, port), username, password, insecure)
        router = router.split('-')[3]
        check_delay(router, results, DELAY_DB)
    create_table_rows(DELAY_DB, ROWS_DB)
    print_table(ROWS_DB)
    end = time.time()
    float_format = '{0:.2F}'
    print(f'Total time: {float_format.format(end - start)} seconds')


if __name__ == "__main__":
    main()
