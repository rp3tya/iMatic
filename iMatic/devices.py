import socket
import binascii
from typing import List
from enum import Enum

CHANNEL_8  = False
CHANNEL_16 = True
CHANNEL_8_COMMANDS  = ["FD022001015D", "FD022001005D", "FD022002015D", "FD022002005D", "FD022003015D", "FD022003005D", "FD022004015D", "FD022004005D", "FD022005015D", "FD022005005D", "FD022006015D", "FD022006005D", "FD022007015D", "FD022007005D", "FD022008015D", "FD022008005D", "FD0220F8885D", "FD0220F8805D"]
CHANNEL_16_COMMANDS = ["580112000000016C", "580111000000016B", "580112000000026D", "580111000000026C", "580112000000036E", "580111000000036D", "580112000000046F", "580111000000046E", "5801120000000570", "580111000000056F", "5801120000000671", "5801110000000670", "5801120000000772", "5801110000000771", "5801120000000873", "5801110000000872", "5801120000000974", "5801110000000973", "5801120000000A75", "5801110000000A74", "5801120000000B76", "5801110000000B75", "5801120000000C77", "5801110000000C76", "5801120000000D78", "5801110000000D77", "5801120000000E79", "5801110000000E78", "5801120000000F7A", "5801110000000F79", "580112000000107B", "580111000000107A", "5801130000FFFF77", "580113000000007B", "5801100000000069"]

class EthernetRelay(object):
    """SainSmart Ethernet Relay.
    <https://www.sainsmart.com/products/network-web-server-16-channels-relay-ethernet-controller-module-remote-control-board-lan-wan-web-server-rj45-port>
    """

    def __init__(self, host='192.168.1.4', port=3000, timeout=10, board_type=CHANNEL_16):
        # type: (str) -> None
        """Initalize the class.
        Kwargs:
            host (str): The IP address of the ethernet relay.
            port (int): The port number of the ethernet relay.
            timeout (int): Communication timeout in seconds.
            board_type (int): Type of relay board.
        Attributes:
            host (str): The IP address of the ethernet relay.
            port (int): The port number of the ethernet relay.
            timeout (int): The connection timeout in seconds.
            relays (:obj:`list` of :obj:`bool`): A list of the on/off state of each relay.
            commands (:obj:`list` of :obj:`str`): A list of the on/off commands of each relay.
        """
        self._host = host
        self._port = port
        self._timeout = timeout
        self._relays = [False] * (8 if board_type == CHANNEL_8 else 16)
        self._commands = CHANNEL_8_COMMANDS if (board_type == CHANNEL_8) else CHANNEL_16_COMMANDS
        # get current state
        self.state()

    def check_index(self, relay_index):
        # type: (int) -> None
        """Check that relay_index is valid.
        This method raises an IndexError if `relay_index` is negative or if
        `relay_index` is greater than or equal to the number of relay.
        Args:
            relay_index (int): the relay index.
        Raises:
            IndexError: If `relay_index` is negative or greater than the
                number of relays.
        """
        if relay_index < 0:
            raise IndexError('relay_index={} cannot be negative'.format(relay_index))
        elif relay_index >= len(self._relays):
            raise IndexError('relay_index={} cannot be greater than {}'.format(
                relay_index, len(self._relays)))

    def state(self):
        # type: () -> List[bool]
        """Get the state of the relays.
        Raises:
            RuntimeError: If there was a problem with requesting the url or
                parsing the resp.
        """
        state_cmd = self._commands[len(self._commands)-1]
        self.control([state_cmd])
        return self._relays

    def verify(self):
        # type: () -> None
        """Verify the state of the relays matches this class instance's state.
        Raises:
            RuntimeError: :func:`EthernetRelay.state()`
            ValueError: If this class instance's state does not match the state
                of the relays.
        """
        state = self.state()
        index = 0
        for i, j in zip(self._relays, state):
            if i != j:
                raise ValueError('Relay at index={} did not match state={}'.format(index, j))
            index += 1

    def toggle(self, relay_index):
        # type: (int) -> None
        """Toggle the state of a relay.
        Args:
            relay_index (int): the relay index to toggle.
        Raises:
            IndexError: :func:`EthernetRelay.check_index`
        """
        self.check_index(relay_index)
        if self._relays[relay_index]:
            self.turn_off(relay_index)
        else:
            self.turn_on(relay_index)

    def turn_on(self, relay_index):
        # type: (int) -> None
        """Turn a relay on.
        Args:
            relay_index (int): the relay index to turn on.
        Raises:
            IndexError: :func:`EthernetRelay.check_index`
        """
        self.check_index(relay_index)
        self.control([self._commands[relay_index*2+0]])
        self._relays[relay_index] = True
        self.verify()

    def turn_off(self, relay_index):
        # type: (int) -> None
        """Turn a relay off.
        Args:
            relay_index (int): the relay index to turn off.
        Raises:
            IndexError: :func:`EthernetRelay.check_index`
        """
        self.check_index(relay_index)
        self.control([self._commands[relay_index*2+1]])
        self._relays[relay_index] = False
        self.verify()

    def all_on(self):
        # type: () -> None
        """Turn all relays on."""
        cmds = []
        for ri in range(len(self._relays)):
            cmds.append(self._commands[ri*2+0])
        self.control(cmds)
        self._relays = [True for r in self._relays]
        self.verify()

    def all_off(self):
        # type: () -> None
        """Turn all relays off."""
        cmds = []
        for ri in range(len(self._relays)):
            cmds.append(self._commands[ri*2+1])
        self.control(cmds)
        self._relays = [False for r in self._relays]
        self.verify()

    def control(self, cmdList):
        # type: (str) -> None
        resp = []
        # send command(s)
        sock = socket.create_connection((self._host, self._port), self._timeout)
        for cmd in cmdList:
            sock.send(binascii.a2b_hex(cmd))
            resp = sock.recv(8)
        sock.close()
        # parse response
        state_bits_str = ""
        if (len(resp) > 2):
            state_bits_str = "{:08b}".format(resp[len(resp)-2]) + state_bits_str
        if (len(resp) > 4):
            state_bits_str = "{:08b}".format(resp[len(resp)-3]) + state_bits_str
        state_bits_str = state_bits_str[::-1]
        # update current relay states
        for ri in range(len(self._relays)):
            self._relays[ri] = (state_bits_str[ri] == '1')

