header_template = """<?xml version='1.0'?> \
<rspec xmlns="http://www.geni.net/resources/rspec/3" type="request" \
generated_by="jFed RSpec Editor" generated="2017-05-04T14:34:20.667+02:00" \
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
component_manager_id="urn:publicid:IDN+twist.tu-berlin.de+authority+am" \
component_id="%s">
  <sliver_type name="raw-pc"/>
  <location xmlns="http://jfed.iminds.be/rspec/ext/jfed/1" x="%f" y="%f"/>
</node>"""
