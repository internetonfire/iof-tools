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
header_template = """<?xml version='1.0'?>
<rspec xmlns="http://www.geni.net/resources/rspec/3" type="request" \
generated_by="jFed RSpec Editor" generated="2017-04-11T14:27:13.049+02:00" \
xmlns:emulab="http://www.protogeni.net/resources/rspec/ext/emulab/1" \
xmlns:delay="http://www.protogeni.net/resources/rspec/ext/delay/1" \
xmlns:jfed-command="http://jfed.iminds.be/rspec/ext/jfed-command/1" \
xmlns:client="http://www.protogeni.net/resources/rspec/ext/client/1" \
xmlns:jfed-ssh-keys="http://jfed.iminds.be/rspec/ext/jfed-ssh-keys/1" \
xmlns:jfed="http://jfed.iminds.be/rspec/ext/jfed/1" \
xmlns:sharedvlan="http://www.protogeni.net/resources/rspec/ext/shared-vlan/1" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.geni.net/resources/rspec/3 \
http://www.geni.net/resources/rspec/3/request.xsd ">"""

footer_template = """</rspec>"""

node_template = """<node client_id="%s" exclusive="true" \
  component_manager_id="urn:publicid:IDN+wall1.ilabt.iminds.be+authority+cm" \
  component_id="%s">
  <sliver_type name="raw-pc">
    <disk_image name="urn:publicid:IDN+wall1.ilabt.iminds.be+image+emulab-ops:UBUNTU18-64-STD"/>
  </sliver_type>
  <location xmlns="http://jfed.iminds.be/rspec/ext/jfed/1" x="%f" y="%f"/>
  <interface client_id="%s:if0">
      <ip address="192.168.0.1" netmask="255.255.255.0" type="ipv4"/>
    </interface>
  <!--hardware_type="%s"-->
</node>\n"""

network_header = """<link client_id="link0">
    <component_manager name="urn:publicid:IDN+wall1.ilabt.iminds.be+authority+cm"/>
"""
network_template = """  <interface_ref client_id="%s:if0"/>\n"""

network_footer = """   <link_type name="lan"/>
  </link>"""