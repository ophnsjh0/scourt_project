import requests
from requests.auth import HTTPBasicAuth
from server_seesion import SessionManager
from prettytable import PrettyTable

server = {'ip':'10.10.10.10', 'id':'administrator@vsphere.local', 'password':'1234qwer'}
vc_host = "10.10.10.10"
vc_user = "administrator@vsphere.local"
vc_password = "1234qwer"

def vcenter_login(server, session):
    session.verify = False
    requests.packages.urllib3.disable_warnings()
    session.headers.update({'Content-Type': 'application/json'})
    url = f'https://{server["ip"]}/rest/com/vmware/cis/session'
    response = session.post(url, auth=HTTPBasicAuth(server['id'], server['password']))
    if response.status_code == 200:
        session_token = response.json()['value']
        print(f"{server['ip']} Login succesful")
        return session_token
    else:
        print(f"{server['ip']} Login Failed: {response.status_code} - {response.text}")
        return None

def vcenter_datacenter(token, session):
    vm_url = f"https://{server['ip']}/rest/vcenter/datacenter/datacenter-3"
    headers = {'vmware-api-session-id': token}
    response = session.get(vm_url, headers=headers, verify=False)
    if response.status_code == 200:
        vms = response.json()
        print(vms)
    else:
        print(f"VM GET FALSE: {response.status_code} - {response.text}")
        return None


def vcenter_cluster(token, session):
    vm_url = f"https://{server['ip']}/rest/vcenter/cluster"
    headers = {"vmware-api-session-id": token}
    response = session.get(vm_url, headers=headers, verify=False)
    if response.status_code == 200:
        vms = response.json()["value"]
        return vms
    else:
        print(f"VM GET FALSE: {response.status_code} - {response.text}")
        return None


def vcenter_host(token, session):
    vm_url = f"https://{server['ip']}/rest/vcenter/host"
    headers = {"vmware-api-session-id": token}
    response = session.get(vm_url, headers=headers, verify=False)
    if response.status_code == 200:
        vms = response.json()["value"]
        return vms
    else:
        print(f"VM GET FALSE: {response.status_code} - {response.text}")
        return None

def vcenter_cluster_in_host(token, session, clusters):
    result = []
    for cluster in clusters:
        vm_url = f"https://{server['ip']}/rest/vcenter/host?filter.clusters={cluster['cluster']}"
        headers = {"vmware-api-session-id": token}
        response = session.get(vm_url, headers=headers, verify=False)
        if response.status_code == 200:
            hosts = response.json()['value']
            cluster['hosts'] = hosts
            result.append(cluster)
        else:
            print(f"VM GET FALSE: {response.status_code} - {response.text}")
            return None

def vcenter_vm(token, session):
    vm_url = f"https://{server['ip']}/rest/vcenter/vm"
    headers = {"vmware-api-session-id": token}
    response = session.get(vm_url, headers=headers, verify=False)
    if response.status_code == 200:
        vms = response.json()
        return vms
    else:
        print(f"VM GET FALSE: {response.status_code} - {response.text}")
        return None

def vcenter_host_in_vm(token, session, cluster_host):
    output = PrettyTable()
    output.field_names = ["cluster", "host", "host-domain", "vm", "cpu_count", "memory_size", "power_state"]
    result = []

    for cluster in cluster_host:
        for host in cluster['hosts']:
            vm_url = f"https://{server['ip']}/rest/vcenter/vm?filter.hosts={host['host']}"
            headers = {"vmware-api-session-id": token}
            response = session.get(vm_url, headers=headers, verify=False)
            if response.status_code == 200:
                vms = response.json()["value"]
                host['vms'] = vms
            else:
                print(f"VM GET FALSE: {response.status_code} - {response.text}")
                return None
    
    for cluster in cluster_host:
        for host in cluster["hosts"]:
            first_row_resource = True
            for vm in host['vms']:
                output.add_row([
                    cluster['name'] if first_row_resource else "",
                    host['host'] if first_row_resource else "",
                    host['name'] if first_row_resource else "",
                    vm['name'],
                    vm['cpu_count'],
                    vm['memory_size_Mib'],
                    vm['power_state'],
                ])
                first_row_resource = False
            output.add_row(["-" * 28, "-" * 12, "-" * 27, "-" * 43, "-" * 11, "-" * 13, "-" * 13])
            
    print(output)
    return cluster_host

def vcenter_datastore(token, session):
    vm_url = f"https://{server['ip']}/rest/vcenter/datastore"
    headers = {"vmware-api-session-id": token}
    response = session.get(vm_url, headers=headers, verify=False)
    if response.status_code == 200:
        vms = response.json()
        for datastore in vms['value']:
            print(datastore)
    else:
        print(f"VM GET FALSE: {response.status_code} - {response.text}")
        return None 


def vcenter_datastore_detail(token, session):
    vm_url = f"https://{server['ip']}/rest/vcenter/datastore/{datastore-1027}"
    headers = {"vmware-api-session-id": token}
    response = session.get(vm_url, headers=headers, verify=False)
    if response.status_code == 200:
        vms = response.json()
        print(vms)
    else:
        print(f"VM GET FALSE: {response.status_code} - {response.text}")
        return None


def vcenter_resource_pool(token, session):
    vm_url = f"https://{server['ip']}/rest/vcenter/resource-pool"
    headers = {"vmware-api-session-id": token}
    response = session.get(vm_url, headers=headers, verify=False)
    if response.status_code == 200:
        vms = response.json()
        print(vms)
    else:
        print(f"VM GET FALSE: {response.status_code} - {response.text}")
        return None


def vcenter_network(token, session):
    vm_url = f"https://{server['ip']}/rest/vcenter/network?filter.dev_svr_service-DVUplinks-2002"
    headers = {"vmware-api-session-id": token}
    response = session.get(vm_url, headers=headers, verify=False)
    if response.status_code == 200:
        vms = response.json()
        print(vms)
    else:
        print(f"VM GET FALSE: {response.status_code} - {response.text}")
        return None


def vcenter_logout(token, session):
    headers = {"vmware-api-session-id": token}
    url = f"https://{server['ip']}/rest/com/vmware/cis/session"
    response = session.delete(vm_url, headers=headers)
    return response.status_code == 204

def export_csv(result):
    file_path = fr'vcenter.csv'
    file = open(file_path, 'w', endoding='utf-8')
    file.write("cluster, host, host-domain, vm, cpu_count, memory_size, power_state")
    for cluster in result:
        for host in cluster['hosts']:
            first_row_resource = True
            for vm in host['vms']:
                file.write(
                    f"{cluster['name'] if first_row_resource else ''}, 
                    {host['host'] if first_row_resource else ''},
                    {host['name'] if first_row_resource else ''},
                    {vm['name']},
                    {vm['cpu_count']},
                    {vm['memory_size_MiB']},
                    {vm['power_state']}\n"
                    )
                first_row_resource = False
    file.close()
    
if __name__ == "__main__":
    session_manager = SessionManager()
    session = session_manager.get_session()
    token = vcenter_login(server, session)
    clusters = vcenter_cluster(token, session)
    cluster_host = vcenter_cluster_in_host(token, session, clusters)
    result = vcenter_host_in_vm(token, session, cluster_host)
    # vcenter_datacenter(token, session)
    # hosts = vcenter_host(token, session)
    # vcenter_network(token, session)
    # vcenter_vm(token, session)
    # vcenter_datastore(token, session)
    export_csv(result)
    
    
