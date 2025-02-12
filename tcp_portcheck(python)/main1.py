import socket

def check_port(ip, port, timeout=2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
        sock.close()
        return True
    except Exception as e:
        return False

def check_ip_ports(ip):
    results = {
        'IP': ip,
        'SSH (Port 22)': check_port(ip, 22),
        'HTTP (Port 80)': check_port(ip, 80),
        'HTTPS (Port 443)': check_port(ip, 443)
    }
    return results

def write_results_to_file(results, filename):
    with open(filename, 'a') as file:
        for result in results:
            file.write(f"Results for {result['IP']}:\n")
            file.write(f"SSH (Port 22): {'Open' if result['SSH (Port 22)'] else 'Closed'}\n")
            file.write(f"HTTP (Port 80): {'Open' if result['HTTP (Port 80)'] else 'Closed'}\n")
            file.write(f"HTTPS (Port 443): {'Open' if result['HTTPS (Port 443)'] else 'Closed'}\n")
            file.write("\n")

def main():
    all_results = []
    ip_addresses = [
                        "10.10.10.10",
                    ]
    for ip in ip_addresses:
        result = check_ip_ports(ip)
        all_results.append(result)
        print(f"Results for {ip}:")
        print(f"SSH (Port 22): {'Open' if result['SSH (Port 22)'] else 'Closed'}")
        print(f"HTTP (Port 80): {'Open' if result['HTTP (Port 80)'] else 'Closed'}")
        print(f"HTTPS (Port 443): {'Open' if result['HTTPS (Port 443)'] else 'Closed'}")
        print()
        
    write_results_to_file(all_results, 'port_check_results.txt')

if __name__ == "__main__":
    main()
