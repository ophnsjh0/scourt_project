import paramiko
from concurrent.futures import ThreadPoolExecutor, as_complete
from cryptography.fernet import Fernet
from prettytable import PrettyTable
import time
import logging
from time import sleep
import json
import re
import os


def load_key():
    return open("secret.key", "rb").read()


def load_and_decrypt_data(filename):
    key = load_key()
    fernet = Fernet(key)

    with open(filename, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = fernet.decrypt(encrypted_data).decode()

    data_list = json.loads(decrypted_data)

    return data_list

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_crc_check_cisco(name, host, username, password, command, retries=3, delay=5):
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
            time.sleep(1)
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

def parse_error_output(name, output):
    result = []
    error = [] 
    sections = re.split(r'\n+', output)
    
    for line in sections:
        if "FCS-Err" in line:
            current_section = 'Error1'
            continue
        elif "Single-Col" in line:
            current_section = 'Error2'
            continue
        elif "OverSize" in line:
            current_section = 'Error3'
            continue
        
        if line.startswith("Te") or line.startswith("Gi") or line.startswith("Po"):
            parts = line.split()
            
            port = parts[0]
            data_parts = parts[1:7]
            if current_section == 'Error1':
                error.append(
                    {
                        'port' : port,
                        'Align-Err' : data_parts[0],
                        'FCS-Err' : data_parts[1],
                        'Xmit-Err' : data_parts[2],
                        'Rcv-Err' : data_parts[3],
                        'UnderSize' : data_parts[4],
                        'OutDiscards' : data_parts[5],
                    }
                )
    
    return error

def create_pretty_table(switch, error_data):
    table = PrettyTable()
    table.title = switch
    table.field_names = ["Interface", "FCS-Err", "OutDiscards", "Align-Err", "Xmit-Err", "Rcv-Err", "UnderSize", "State"]
    
    abnormal_metrics = []
    for error in error_data:
        state = "정상"
        for error_name, error_val in error.items():
            if error_name != 'port' and error_val != '0':
                state = f"비정상({error_name})"
                
        table.add_row(
            [
                error['port'],
                error['FCS-Err'],
                error['OutDiscards'],
                error['Align-Err'],
                error['Xmit-Err'],
                error['Rcv-Err'],
                error['UnderSize'],
                state
            ]
        )
        
    print(table)
    print("\n")
    
def create_pretty_table_occur(switch, error_data):
    table = PrettyTable()
    table.title = switch
    table.field_names = ["Interface", "FCS-Err", "OutDiscards", "Align-Err", "Xmit-Err", "Rcv-Err", "UnderSize", "State"]
    
    abnormal_metrics = []
    for error in error_data:
        state = "정상"
        for error_name, error_val in error.items():
            if error_name != 'port' and error_val != '0':
                state = f"비정상({error_name})"
        if '비정상' in state:       
            table.add_row(
                [
                    error['port'],
                    error['FCS-Err'],
                    error['OutDiscards'],
                    error['Align-Err'],
                    error['Xmit-Err'],
                    error['Rcv-Err'],
                    error['UnderSize'],
                    state
                ]
            )
        
    print(table)
    print("\n")

def main():
    devices = load_and_decrypt_data("encrypted_list.bin")
    command = "show interface count error"
    results = []
    
    max_workers = min(32, (os.cpu_count() or 1) + 4)
    logging.info(f"Using {max_workers} threads for SSH connections.")
    
    with ThreadPoolExecutor(max_workers=max_workers) as excutor:
        future_to_device = {
            excutor.submit(get_crc_check_cisco, device['name'], device['ip'], device['id'], device['password'], command): device for device in devices
        }
        
        for future in as_complete(future_to_device):
            device = future_to_device[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                results.append({'host': device['host'], 'output' : None, 'error' : str(exc)})
                
    for result in results:
        host = result['host']
        if result['error']:
            print(f"Error connecting to {host}: {result['error']}\n")
        else:
            error_data = parse_error_output(result['name'], result['output'])
            create_pretty_table_occur(result['name'], error_data)
            # create_pretty_table(result['name'], error_data)

if __name__ == "__main__":
    main()
