import paramiko
import time

class SSHManager:
    def __init__(self, switch):
        self.switch = switch
        self.ssh_client = paramiko.SSHClient()
        
    def login(self)
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh_client.connect(
                hostname=self.switch['ip'],
                port=22,
                username=self.switch['id'],
                password=self.switch['password'],
                look_for_keys=False,
                allow_agent=False,
            )
            print(f"{self.switch['name']} Login Successful")
            return self.ssh_client
        except paramiko.SSHException as e:
            print(f"{self.switch['name']} Login Failed: {e}")
            return None
        
    def exec_command(self, command):
        if self.ssh_client is None:
            raise Exception("Connection not established.")
        else:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            data = stdout.read().decode('utf-8')
            print(f"{self.switch['name']} get interface : ok")
            return data
        
    def logout(self):
        if self.ssh_client:
            self.ssh_client.close()
            print(f"{self.switch['name']} Logout Successful")
        else:
            print(f"{self.switch['name']} Logoout Failed: Not SSH_Client")
    