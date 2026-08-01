# Auto-generated Code Vault for 'TcpPortScanner' [Python]

import socket
import concurrent.futures
import argparse
import time

class TcpPortScanner:
    def __init__(self, target_ip):
        self.target_ip = target_ip

    def scan_port(self, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((self.target_ip, port))
                return port
        except (socket.error, ConnectionRefusedError):
            return None

    def scan_ports(self, start_port, end_port):
        open_ports = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(self.scan_port, port): port for port in range(start_port, end_port + 1)}
            for future in concurrent.futures.as_completed(futures):
                port = futures[future]
                try:
                    result = future.result()
                    if result is not None:
                        open_ports.append(result)
                except Exception as e:
                    print(f"Error scanning port {port}: {e}")
        return open_ports

def main():
    parser = argparse.ArgumentParser(description="TCP Port Scanner")
    parser.add_argument("-t", "--target", help="Target IP address", required=True)
    args = parser.parse_args()
    target_ip = args.target
    scanner = TcpPortScanner(target_ip)
    start_time = time.time()
    open_ports = scanner.scan_ports(1, 1024)
    end_time = time.time()
    print(f"Open ports on {target_ip}: {open_ports}")
    print(f"Scan completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
