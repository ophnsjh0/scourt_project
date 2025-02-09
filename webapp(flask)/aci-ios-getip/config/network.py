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

def aci_findport(center, token, session):
    requests.packages.urllib3.disable_warnings()
    session.headers.update(token)
    
    page_size=1000
    imdata = []
    page = 0
    
    while True:
        url = f'https://{center["ip"]}/api/node/class/infraPortSummary.json?page-size={page_size}&page={page}&order-by=infraPortSummary.dn'
        response = session.get(url, verify=False)
        try:
            response.json()['imdata'][0]
            for item in response.json()['imdata']:
                imdata.append(item)
        except:
            break
        page += 1
        
    return { "imdata" : imdata }

def ciscol2_net(name, network, host, username, password, commands, retries=3, delay=5):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    for attempt in range(1, retries + 1):
        try:
            logging.info(f"[{host}] SSH 연결 시도 ({attempt}/{retries})..." )
            ssh.connect(hostname=host, username=username, password=password, look_for_keys=False, allow_agent=False)
            logging.info(f"[{host}] SSH 연결 성공")
            
            remote_conn = ssh.invoke_shell()
            #time.sleep(1)
            
            remote_conn.send("terminal length 0\n")
            #time.sleep(1)
            output = remote_conn.recv(65535).decode('utf-8')
            logging.debug(f"[{host}] Teminal length 0 응답: {output}")
            
            for command in commands:
                remote_conn.send(command + '\n')
                #time.sleep(3)
                buffer = ""
                timeout = 10 
                end_time = time.time() + timeout
            
            while True:
                if remote_conn.recv_ready():
                    data = remote_conn.recv(1024).decode('utf-8')
                    buffer += data
                    end_time = time.time() + timeout
                    logging.debug(f"[{host}] 데이터 수신: {data}")
                else:
                    time.sleep(0.5)
                    
                if time.time() > end_time:
                    break
                
            remote_conn.send("\n")
            # time.sleep(1)
            prompt = remote_conn.recv(65535).decode('utf-8')
            logging.debug(f"[{host}] 프롬프트 확인 : {prompt}")
            ssh.close()
            logging.info(f"[{host}] 명령어 실행 완료")
            
            return {'name': name, 'host': host, 'output': buffer, 'error': None}
            
        except paramiko.AuthenticationException:
            logging.error(f"[{host}] 인증 실패")
            return {'host': host, 'output': None, 'error': "Authentication failed"}
        except paramiko.SSHException as sshException:
            logging.error(f"[{host}] SSH 연결 실패: {sshException}")
            if attempt < retries:
                logging.info(f"[{host}] 재시도 대기: {delay}초")
                sleep(delay)
            else:
                return {'host': host, 'output': None, 'error': f'SSH Connection failed: {sshException}'}
        except Exception as e:
            logging.error(f"[{host}] 오류 발생: {e}")
            if attempt < retries:
                logging.info(f"[{host}] 재시도 대기: {delay}초")
                sleep(delay)
            else:
                return {'host': host, 'output': None, 'error': f'Error: {e}'}
    return {'host': host, 'output': None, 'error': 'Failed after multiple attempts'}
