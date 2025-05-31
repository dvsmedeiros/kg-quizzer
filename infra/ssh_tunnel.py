import sshtunnel

class SSHTunnel:
    def __init__(self, ssh_host, ssh_port, target_host, target_port, ssh_username=None, ssh_password=None, ssh_pkey=None):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.ssh_pkey = ssh_pkey
        self.target_host = target_host
        self.target_port = target_port
        self.tunnel = None

    def __enter__(self):
        self.open_ssh_tunnel()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_ssh_tunnel()

    def open_ssh_tunnel(self):
        self.tunnel = sshtunnel.SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username=self.ssh_username,
            ssh_password=self.ssh_password,
            ssh_pkey=self.ssh_pkey,
            remote_bind_address=(self.target_host, self.target_port),
            local_bind_address=('0.0.0.0', 0)
        )
        self.tunnel.start()

    def get_local_port(self):
        return self.tunnel.local_bind_port

    def close_ssh_tunnel(self):
        if self.tunnel:
            self.tunnel.stop()

    def __del__(self):
        self.close_ssh_tunnel()
