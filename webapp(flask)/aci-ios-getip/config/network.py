import paramiko
import requests
import logging
import re
import time
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def aci_bd(center, token, session):
    requests.packages.urllib3.disable_warnings()
    session.headers.update(token)
    url = f'https://{center['ip']}/api/node/class/fvBD.json?rsp-subtree=children&rsp-subtree-class=fvSubnet&order-by=fvBD.dn'
    response = session.get(url, verify=False)
    if response.status_code == 200:
        result = response.json()['imdata']
        return result
    else:
        print(f"{center['name']} get bd_info : Failed")
        exit()
        
def aci_findip(center, token, session, tenant, bd, serial):
    requests.packages.urllib3.disable_warnings()
    session.headers.update(token)
    
    # url = f'https://{center["ip"]}/api/node/mo/uni/tn-Operation/ap-backend_ap/epg-int_nas_56.json?query-target=chidren&target-subtree-class=fvCEp&rsp-subtree=chidren&rsp-subtree-class=fvIp'
    # url = f'https://{center["ip"]}/api/node/class/fvCEp.json?query-target-filter=and(eq(fvCEp.bdDn,"uni/tn-{tenant}/BD-{bd}))&rsp-subtree=children&rsp-subtree-class=fvIp&order-by=fvCEp.dn'
    # url = f'https://{center["ip"]}/api/node/class/fvCEp.json?rsp-subtree=children&rsp-subtree-class=fvIp,fvRsCEpToPathEp&order-by=fvCEp.dn'
    # url = f'https://{center["ip"]}/api/node/class/fvCEp.json?rsp-subtree=children&rsp-subtree-class=fvIp&order-by=fvCEp.dn'
    # query-target-filter=and(eq(fvIp.addr, "172.25.1"))&
    
    if serial == 'serial':
        url = f'https://{center["ip"]}/api/node/class/fvCEp.json?rsp-subtree=children&rsp-subtree-class=fvIp&order-by=fvCEp.dn'
    else:
        url = f'https://{center["ip"]}/api/node/class/fvCEp.json?query-target-filter=and(eq(fvCEp.bdDn,"uni/tn-{tenant}/BD-{bd}))&rsp-subtree=children&rsp-subtree-class=fvIp&order-by=fvCEp.dn'

    response = session.get(url, verify=False)
    if response.status_code == 200:
        result = response.json()['imdata']
        return result
    else:
        print(f"{center['name']} get bd_info : Failed")
        exit()