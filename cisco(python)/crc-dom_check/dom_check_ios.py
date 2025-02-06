import paramiko
from concurrent.futures import ThreadPoolExecutor, as_completed
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


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_transceiver_details(name, host, username, password, command, retries=3, delay=5):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for attempt in range(1, retries + 1):
        try:
            logging.info(f"[{host}] SSH 연결 시도 ({attempt}/{retries})...")
            ssh.connect(
                hostname=host,
                username=username,
                password=password,
                look_for_keys=False,
                allow_agent=False,
            )
            logging.info(f"[{host}] SSH 연결 성공")

            remote_conn = ssh.invoke_shell()
            # time.sleep(1)

            remote_conn.send("terminal length 0\n")
            # time.sleep(1)
            output = remote_conn.recv(65535).decode("utf-8")
            logging.debug(f"[{host}] Teminal length 0 응답: {output}")

            remote_conn.send(command + "\n")
            if name == '결과 느린장비':
                time.sleep(20)
            else:
                time.sleep(10)
            # time.sleep(3)
            buffer = ""
            timeout = 10
            end_time = time.time() + timeout

            while True:
                if remote_conn.recv_ready():
                    data = remote_conn.recv(1024).decode("utf-8")
                    buffer += data
                    end_time = time.time() + timeout
                    logging.debug(f"[{host}] 데이터 수신: {data}")
                else:
                    time.sleep(0.5)

                if time.time() > end_time:
                    break

            remote_conn.send("\n")
            time.sleep(1)
            prompt = remote_conn.recv(65535).decode("utf-8")
            logging.debug(f"[{host}] 프롬프트 확인 : {prompt}")
            ssh.close()
            logging.info(f"[{host}] 명령어 실행 완료")

            return {"name": name, "host": host, "output": buffer, "error": None}

        except paramiko.AuthenticationException:
            logging.error(f"[{host}] 인증 실패")
            return {"host": host, "output": None, "error": "Authentication failed"}
        except paramiko.SSHException as sshException:
            logging.error(f"[{host}] SSH 연결 실패: {sshException}")
            if attempt < retries:
                logging.info(f"[{host}] 재시도 대기: {delay}초")
                sleep(delay)
            else:
                return {
                    "host": host,
                    "output": None,
                    "error": f"SSH Connection failed: {sshException}",
                }
        except Exception as e:
            logging.error(f"[{host}] 오류 발생: {e}")
            if attempt < retries:
                logging.info(f"[{host}] 재시도 대기: {delay}초")
                sleep(delay)
            else:
                return {"host": host, "output": None, "error": f"Error: {e}"}
    return {"host": host, "output": None, "error": "Failed after multiple attempts"}

def determine_state(metrics):
    abnormal_metrics = []
    
    for metric_name, metric_values in metrics.items():
        current = metric_values.get('Current')
        high_alarm = metric_values.get('High Alarm')
        low_alarm = metric_values.get('Low Alarm')
        
        if current == 'N/A' or high_alarm == 'N/A' or low_alarm == 'N/A':
            abnormal_metrics.append(metric_name)
            continue
        
        if current > high_alarm or current < low_alarm:
            abnormal_metrics.append(metric_name)
            
    if abnormal_metrics:
        return f"비정상 ({', '.join(abnormal_metrics)})"
    
    return '정상'

def parse_transceiver_output(name, output):
    result = []
    temp = {}
    volt = {}
    current = {}
    rx_power = {}
    tx_power = {}

    sections = re.split(r'\n+', output)

    current_section = None

    for line in sections:
        line = line.strip()

        if not line:
            continue

        if line.startswith("Temperature"):
            current_section = 'Tempaerature'
            continue
        elif line.startswith('Voltage'):
            current_section = ' Voltage'
            continue
        elif line.startswith('Current'):
            current_section = 'Current'
            continue
        elif line.startswith('Transmit Power'):
            current_section = "Transmit Power"
            continue
        elif line.startswith('Receive Power'):
            current_section("Receive Power")
            continue
        elif line.startswith("Port") and current_section:
            continue
        elif line.startswith("---------"):
            continue

        if current_section and line.startswith("Te"):
            parts = line.split()
            if current_section == 'Transmit Power' or current_section == 'Current' or current_section == 'Receive Power':
                if len(parts) < 7:
                    print(f"데이터 형식이 올바르지 않습니다:{line}")
                    continue
                port = parts[0]
                lane = parts[1]
                data_parts = part[2:7]
            else:
                if len(parts) < 6:
                    print(f"데이터 형식이 올바르지 않습니다:{line}")
                    continue
                port = parts[0]
                data_parts = parts[1:6]

            values = []

            for part in data_parts:
                if part.upper() == 'N/A':
                    values.append(None)
                else:
                    try:
                        values.append((float(part)))
                    except ValueError:
                        print(f"포트 {port }의 값을 변환하는데 실패했습니다.")
                        values.append(None)

            if current_section == 'Temperature':
                temp[port] = {
                    "Current": values[0] if values[0] is not None else "N/A",
                    "High Alarm": values[1] if values[1] is not None else "N/A",
                    "High Warn": values[2] if values[2] is not None else "N/A",
                    "Low Warn": values[3] if values[3] is not None else "N/A",
                    "Low Alarm": values[4] if values[4] is not None else "N/A",
                }
            elif current_section == "Voltage":
                temp[port] = {
                    "Current": values[0] if values[0] is not None else "N/A",
                    "High Alarm": values[1] if values[1] is not None else "N/A",
                    "High Warn": values[2] if values[2] is not None else "N/A",
                    "Low Warn": values[3] if values[3] is not None else "N/A",
                    "Low Alarm": values[4] if values[4] is not None else "N/A",
                }
            elif current_section == "Current":
                temp[port] = {
                    "Current": values[0] if values[0] is not None else "N/A",
                    "High Alarm": values[1] if values[1] is not None else "N/A",
                    "High Warn": values[2] if values[2] is not None else "N/A",
                    "Low Warn": values[3] if values[3] is not None else "N/A",
                    "Low Alarm": values[4] if values[4] is not None else "N/A",
                }
            elif current_section == "Transmit Power":
                temp[port] = {
                    "Current": values[0] if values[0] is not None else "N/A",
                    "High Alarm": values[1] if values[1] is not None else "N/A",
                    "High Warn": values[2] if values[2] is not None else "N/A",
                    "Low Warn": values[3] if values[3] is not None else "N/A",
                    "Low Alarm": values[4] if values[4] is not None else "N/A",
                }
            elif current_section == "Receive Power":
                temp[port] = {
                    "Current": values[0] if values[0] is not None else "N/A",
                    "High Alarm": values[1] if values[1] is not None else "N/A",
                    "High Warn": values[2] if values[2] is not None else "N/A",
                    "Low Warn": values[3] if values[3] is not None else "N/A",
                    "Low Alarm": values[4] if values[4] is not None else "N/A",
                }
    
    dom_data = {
        'temp': [temp],
        'volt': [volt],
        'current': [current],
        'tx_power': [tx_power],
        'rx_power': [rx_power],
    }
    
    switch_dom_data = {
        'switch': name,
        'dom_data': [dom_data]
    }

    result.append(switch_dom_data)
    return result

def create_pretty_table(switch, dom_data):
    temp_data = dom_data[0].get('temp', [{}][0])
    volt_data = dom_data[0].get("volt", [{}][0])
    current_data = dom_data[0].get("current", [{}][0])
    rx_power_data = dom_data[0].get("rx_power", [{}][0])
    tx_power_data = dom_data[0].get("tx_power", [{}][0])

    ports = set(temp_data.keys()).union(
        volt_data.keys(),
        current_data.keys(),
        rx_power_data.keys(),
        tx_power_data.keys(),
    )

    table = PrettyTable()
    table.title = switch
    table.field_names = ["Port", "rx_power", "tx_power", "volt", "temp", "current", "state"]

    for port in sorted(ports):
        rx_p = rx_power_data.get(port, {}).get('Current', 'N/A')
        tx_p = rx_power_data.get(port, {}).get("Current", "N/A")
        volt_p = rx_power_data.get(port, {}).get('Current', 'N/A')
        temp_p = rx_power_data.get(port, {}).get('Current', 'N/A')
        current_p = rx_power_data.get(port, {}).get("Current", "N/A")

        metrincs = {
            "rx_power": rx_power_data.get(port, {}),
            "tx_power": tx_power_data.get(port, {}),
            "volt": volt_data.get(port, {}),
            "temp_p": temp_data.get(port, {}),
            "current_p": current_data.get(port, {}),
        }
        
        state = determine_state(metrics)
        if rx_p == 'N/A' and tx_p == 'N/A':
            state = 'Disable'
        elif rx_p == int(-40.0):
            state = 'Notconnect'
            
        table.add_row(
            [
                port,
                rx_p,
                tx_p,
                volt_p,
                temp_p,
                current_p,
                state
            ]
        )
    
    print(table)
    print("\n")

def create_pretty_table_occur(switch, dom_data):
    temp_data = dom_data[0].get("temp", [{}][0])
    volt_data = dom_data[0].get("volt", [{}][0])
    current_data = dom_data[0].get("current", [{}][0])
    rx_power_data = dom_data[0].get("rx_power", [{}][0])
    tx_power_data = dom_data[0].get("tx_power", [{}][0])

    ports = set(temp_data.keys()).union(
        volt_data.keys(),
        current_data.keys(),
        rx_power_data.keys(),
        tx_power_data.keys(),
    )

    table = PrettyTable()
    table.title = switch
    table.field_names = [
        "Port",
        "rx_power",
        "tx_power",
        "volt",
        "temp",
        "current",
        "state",
    ]

    for port in sorted(ports):
        rx_p = rx_power_data.get(port, {}).get("Current", "N/A")
        tx_p = rx_power_data.get(port, {}).get("Current", "N/A")
        volt_p = rx_power_data.get(port, {}).get("Current", "N/A")
        temp_p = rx_power_data.get(port, {}).get("Current", "N/A")
        current_p = rx_power_data.get(port, {}).get("Current", "N/A")

        metrincs = {
            "rx_power": rx_power_data.get(port, {}),
            "tx_power": tx_power_data.get(port, {}),
            "volt": volt_data.get(port, {}),
            "temp_p": temp_data.get(port, {}),
            "current_p": current_data.get(port, {}),
        }

        state = determine_state(metrics)
        if rx_p == "N/A" and tx_p == "N/A":
            state = "Disable"
        elif rx_p == int(-40.0):
            state = "Notconnect"

        if '비정상' in state:
            table.add_row(
                [
                    port, 
                    rx_p, 
                    tx_p, 
                    volt_p, 
                    temp_p, 
                    current_p, 
                    state,
                ]
            )

    print(table)
    print("\n")


def main():
    devices = load_and_decrypt_data("encrypted_list.bin")
    command = "show interface transceiver detail"
    results = []

    max_workers = min(32, (os.cpu_count() or 1) + 4)
    logging.info(f"Using {max_workers} threads for SSH connections.")

    with ThreadPoolExecutor(max_workers=max_workers) as excutor:
        future_to_device = {
            excutor.submit( get_transceiver_details, device["name"], device["ip"], device["id"], device["password"], command,): device
            for device in devices
        }

        for future in as_completed(future_to_device):
            device = future_to_device[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                results.append(
                    {"host": device["host"], "output": None, "error": str(exc)}
                )

    for result in results:
        host = result["host"]
        if result["error"]:
            print(f"Error connecting to {host}: {result['error']}\n")
        else:
            dom_data = parse_transceiver_output(result["name"], result["output"])
            create_pretty_table_occur(result["name"], dom_data[0['dom_data']])
            # create_pretty_table(result['name'], error_data)


if __name__ == "__main__":
    main()
