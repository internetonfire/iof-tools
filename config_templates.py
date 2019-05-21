from os import chmod
from shutil import copyfile
from os.path import expanduser
from stat import S_IWUSR, S_IRUSR

IDENTITY_FILE = "id.cert"


class SSHConfig:

    def __init__(self, ssh_config, host_config, identity_file,
                 proxy_command=None):
        self.ssh_config = ssh_config
        self.host_config = host_config
        with open(ssh_config, "r") as ssh_file:
            self.ssh_template = ssh_file.read()
        with open(host_config, "r") as host_file:
            self.host_template = host_file.read()
        if proxy_command is not None:
            with open(proxy_command) as proxy_file:
                self.proxy_template = proxy_file.read()
        else:
            self.proxy_template = ""
        # copy the identity file locally
        copyfile(expanduser(identity_file), IDENTITY_FILE)
        chmod(IDENTITY_FILE, S_IWUSR | S_IRUSR)
        self.config = self.ssh_template.format(identity=IDENTITY_FILE)

    def add_host(self, name, hostname):
        self.config += self.host_template.format(name=name, hostname=hostname,
                                                 identity=IDENTITY_FILE,
                                                 proxy=self.proxy_template)

    def __str__(self):
        return self.config


class AnsibleConfig:
    def __init__(self, ansible_config, inventory_config, host_config,
                 inventory_filename, ssh_config_filename):
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
        config = self.ansible_template.format(identity=IDENTITY_FILE,
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
