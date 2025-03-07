import re
import os
import glob
import paramiko
import subprocess
import json
import fnmatch
from datetime import datetime

# 앤서블 vault를 통한 접속 장비 암호화
# ansible-vault encrypt [파일명]

def decrypt_vault(file_path):
    result = subprocess.run(
        ['ansible-vault', 'view', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    if result.returncode == 0:
        file_content = result.stdout.decode().splitlines()
        return file_content
    else:
        print(f"Failed to view {file_path}.")
        print(result.stderr.decode())
        return None

def download_file_via_sftp(decrypt_content):
    now = datetime.now()
    today_date = now.strftime("%Y-%m-%d")
    formatted_date = today_date[2:]
    servers = decrypt_content
    for server in servers:
        host = server['host']
        ip = server['ip']
        user = server['id']
        pw = server['pw']
        port = '22'
        # remote 서버의 file 위치
        remote_base_dir = '/home/sysadm/emergency/'
        remote_dir_pattern = f"{host}_{formatted_date}_*"
        remote_file_name = f"{host}_report_{formatted_date}"
        # local_path 파일을 저장할 위치 위치
        local_path = f"/APP/ansible/playbook/result/{formatted_date}/{host}_report_{formatted_date}.txt"

        ssh = paramiko.SSHClient()
        ssh.set_missiong_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(ip, port, user, pw)

        sftp = ssh.open_sftp()
        remote_dir_list = sftp.listdir(remote_base_dir)
        matching_dirs = fnmatch.filter(remote_dir_list, remote_dir_pattern)

        for directory in matching_dirs:
            remote_dir = os.path.join(remote_base_dir, directory)
            remote_path = os.path.join(remote_dir, remote_file_name)
            
        try:
            if not os.path.exists(os.path.dirname(local_path)):
                os.makedirs(os.path.dirname(local_path))
                
            sftp.get(remote_path, local_path)
            print(f"Downloaded {remote_path} to {local_path}")
        finally:
            sftp.close()
            ssh.close()

def open_file():
    now = datetime.now()
    today_date = now.strftime("%Y-%m-%d")
    formatted_date = today_date[2:]
    all_data = []
    folder_path = f"/APP/ansible/playbook/result/{formatted_date}/"
    file_list = sorted(glob.glob(os.path.join(folder_path, '*_report_*.txt')))
    
    for file in file_list:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.readlines()
            all_data.append(data)
            
    return all_data

def paser_file(all_data):
    now = datetime.now()
    today_date = now.strftime("%Y-%m-%d")
    path = fr"/APP/ansible/playbook/result/{formatted_date}/report_{today_date}.csv"
    file = open(path, 'w', encoding='utf-8')
    file.write(
        f"hostname, CPU, CPU_Used, Memory, Memory_Used, filesystem, IP, Route, LAN, LAN_Speed, NTP, Uptime, Uptime_Day, Inode, IPtable, Fdisk, Crontab, Passwd, Group, Resolv, FsTab, Hosts, Ulimit, Version, Network\n"   
    )

    for file_data in all_data:
        hostname = [word for line in file_data for word in line.split()]
        cpu = [word for line in file_data if 'CPU' in line for word in line.split()]
        memory = [word for line in file_data if "Memory" in line for word in line.split()]
        ip_add = [word for line in file_data if "IP_Address" in line for word in line.split()]
        route = [word for line in file_data if "Routing_Table" in line for word in line.split()]
        lan = [word for line in file_data if "LAN_Check" in line for word in line.split()]
        lan_speed = [
            word for line in file_data if "LAN_Speed" in line for word in line.split()
        ]
        ntp = [word for line in file_data if "NTP_Check" in line for word in line.split()]
        uptime = [word for line in file_data if "Uptime_Check" in line for word in line.split()]
        inode = [word for line in file_data if "inode_check" in line for word in line.split()]
        iptable = [word for line in file_data if "iptables" in line for word in line.split()]
        fdisk = [word for line in file_data if "fdisk-l" in line for word in line.split()]
        cron = [word for line in file_data if "crontab" in line for word in line.split()]
        passwd = [word for line in file_data if "passwd" in line for word in line.split()]
        group = [word for line in file_data if "group" in line for word in line.split()]
        resolv = [word for line in file_data if "resolv.conf" in line for word in line.split()]
        fstab = [word for line in file_data if "fstab" in line for word in line.split()]
        host = [word for line in file_data if "hosts" in line for word in line.split()]
        ulimit = [word for line in file_data if "ulimit-a" in line for word in line.split()]
        version = [word for line in file_data if "unam-a" in line for word in line.split()]
        network = [word for line in file_data if "/etc/sysconfig" in line for word in line.split()]
        file_info = [word for line in file_data if "Filesystem" in line for word in line.split()]
        file.write(
            f"{hostname[0].strip()}, {cpu[2]}, {cpu[4]}%, {memory[2]}, {memory[5]}%, {file_info[2]}, {ip_add[2]}, {route[2]}, {lan[2]}, {lan_speed[2]}, {ntp[2]}, {uptime[2]}, {uptime[3].rstrip(',')}, {inode[2]}, {iptable[2]}, {fdisk[2]}, {cron[2]}, {passwd[2]}, {group[2]}, {resolv[2]}, {fstab[2]}, {host[2]}, {ulimit[2]}, {version[2]}, {network[2]}\n"
        )
    file.close()
    
if __name__ == "__main__":
    vault_file = 'server_info_test.txt'
    decrypt_content = decrypt_vault(vault_file)
    download_file_via_sftp(decrypt_content)
    all_data = open_file()
    paser_file(all_data)
