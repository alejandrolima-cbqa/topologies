
from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()


class Firewall(object):
    """
    A Firewall object is created for each switch that connects.
    A Connection object for that switch is passed to the __init__ function.
    """

    def __init__(self, connection):
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)

        # add switch rules here
        #ICMP RULE
        connection.send(of.ofp_flow_mod(action=of.ofp_action_output(port=of.OFPP_FLOOD),priority=10,match=of.ofp_match(dl_type=0x0800, nw_proto=pkt.ipv4.ICMP_PROTOCOL)))	
        #ARP rule
        connection.send(of.ofp_flow_mod(action=of.ofp_action_output(port=of.OFPP_FLOOD),priority=9,match=of.ofp_match(dl_type=0x0806)))
        
        #RULES BACK
        self.connection.send(of.ofp_flow_mod(action=of.ofp_action_output(port=of.OFPP_IN_PORT),priority=8,match=of.ofp_match(dl_type=0x86dd)))
        self.connection.send(of.ofp_flow_mod(action=of.ofp_action_output(port=of.OFPP_IN_PORT),priority=7,match=of.ofp_match(dl_type=0x0800)))

    def _handle_PacketIn(self, event):
        """
        Packets not handled by the router rules will be
        forwarded to this method to be handled by the controller
        """

        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp  # The actual ofp_packet_in message.
        print("Unhandled packet :" + str(packet.dump()))


def launch():
    """
    Starts the component
    """

    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Firewall(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
