class SSHConfig:

    def __init__(self, ssh_config, host_config, identity_file):
        self.ssh_config = ssh_config
        self.host_config = host_config
        with open(ssh_config, "r") as ssh_file:
            self.ssh_template = ssh_file.read()
        with open(host_config, "r") as host_file:
            self.host_template = host_file.read()
        self.identity_file = identity_file
        self.config = self.ssh_template.format(identity=identity_file)

    def add_host(self, name, hostname):
        self.config += self.host_template.format(name=name, hostname=hostname,
                                                 identity=self.identity_file)

    def __str__(self):
        return self.config


class AnsibleConfig:
    def __init__(self, ansible_config, inventory_config, host_config,
                 identity_filename, inventory_filename, ssh_config_filename):
        self.ansible_config = ansible_config
        self.inventory_config = inventory_config
        self.host_config = host_config
        self.inventory_filename = inventory_filename
        self.ssh_config_filename = ssh_config_filename
        with open(ansible_config, "r") as ansible_file:
            self.ansible_template = ansible_file.read()
        with open(inventory_config, "r") as inventory_file:
            self.inventory_template = inventory_file.read()
        with open(host_config, "r") as host_file:
            self.host_template = host_file.read()
        self.identity_filename = identity_filename
        config = self.ansible_template.format(identity=identity_filename,
                                              inventory=inventory_filename,
                                              ssh_config=ssh_config_filename)
        inventory = self.inventory_template
        self.config = config
        self.inventory = inventory

    def add_host(self, name):
        self.inventory += self.host_template.format(name=name)

    def get_ansible_config(self):
        return self.config

    def get_ansible_inventory(self):
        return self.inventory
