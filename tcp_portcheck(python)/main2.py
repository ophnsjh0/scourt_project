import socket


def tcp_connection(item, timeout=2):
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.create_connection((item, port))
        sock.close()
        return True
    except (socket.timeout, socket.error:
        return False

def export_file(result_data):
    file_path = fr'C:\result\result.csv'
    file = open(file_path, 'w', encording='utf-8')
    file.write("IP, TCP_Port, Result")
    for item in result_data:
        file.write(f"P{item[0]}, {item[1]}, {item[2]}")
        
db = [
    "192.168.1.1",
]
port = [80, 443, 22]

result_data = []

for item in db:
    for port in ports:
        if tcp_connection(item, port):
            ip = item
            tcp = port
            result = '접속가능'
            result_data.append((ip, tcp, result))
            print(f"IP: {ip}, port: {tcp} 접속가능")
        else:
            ip = item
            tcp = port
            result = '접속불가능'
            result_data.append((ip, tcp, result))
            print(f"IP: {ip}, port: {tcp} 접속불가능")
            
for a in result_data:
    print(a)
export_file(result_data)