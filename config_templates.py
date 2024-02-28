#==============================================================================
# Copyright (C) 2019-2024 Mattia Milani, Leonardo Maccari, Luca Baldesi, Lorenzo Ghiro, Michele Segata, Marco Nesler 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#==============================================================================
from os import chmod
from shutil import copyfile
from os.path import expanduser
from stat import S_IWUSR, S_IRUSR

IDENTITY_FILE = "id.cert"


class SSHConfig:

    def __init__(self, ssh_config, host_config, identity_file, user,
                 proxy_command=None):
        self.ssh_config = ssh_config
        self.host_config = host_config
        self.user = user
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
        self.config = self.ssh_template.format(identity=IDENTITY_FILE,
                                               user=user)

    def add_host(self, name, hostname):
        self.config += self.host_template.format(name=name, hostname=hostname,
                                                 identity=IDENTITY_FILE,
                                                 proxy=self.proxy_template,
                                                 user=self.user)

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
