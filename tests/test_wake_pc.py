"""Pure unit tests: never send a network packet."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

FILE = Path(__file__).resolve().parents[1] / 'scripts' / 'termux' / 'wake_pc.py'
SPEC = importlib.util.spec_from_file_location('wake_pc', FILE)
assert SPEC and SPEC.loader
wake_pc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wake_pc)


class TestWakeOnLan(unittest.TestCase):
    def test_mac_forms(self):
        self.assertEqual(wake_pc.normalize_mac('aa:bb:cc:dd:ee:ff'), bytes.fromhex('aabbccddeeff'))
        self.assertEqual(wake_pc.normalize_mac('AA-BB-CC-DD-EE-FF'), bytes.fromhex('aabbccddeeff'))
        self.assertEqual(wake_pc.normalize_mac('aabbccddeeff'), bytes.fromhex('aabbccddeeff'))

    def test_invalid_mac(self):
        for bad in ('', 'REPLACE_WITH_PC_ETHERNET_MAC', 'aa:bb', 'invalid-sequence'):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                wake_pc.normalize_mac(bad)

    def test_magic_packet_bytes(self):
        packet = wake_pc.make_magic_packet('00:11:22:33:44:55')
        self.assertEqual(len(packet), 102)
        self.assertEqual(packet[:6], b'\xff' * 6)
        self.assertEqual(packet[6:], bytes.fromhex('001122334455') * 16)

    def test_send_uses_broadcast_socket_without_network(self):
        with patch.object(wake_pc.socket, 'socket') as mock_socket:
            wake_pc.send_packet('00:11:22:33:44:55', '255.255.255.255', 9)
            instance = mock_socket.return_value.__enter__.return_value
            instance.setsockopt.assert_called_once_with(wake_pc.socket.SOL_SOCKET, wake_pc.socket.SO_BROADCAST, 1)
            instance.sendto.assert_called_once()
            data, destination = instance.sendto.call_args.args
            self.assertEqual(len(data), 102)
            self.assertEqual(destination, ('255.255.255.255', 9))

    def test_reject_bad_destination(self):
        with self.assertRaises(ValueError):
            wake_pc.send_packet('00:11:22:33:44:55', 'NOT_AN_IP', 9)
        with self.assertRaises(ValueError):
            wake_pc.send_packet('00:11:22:33:44:55', '255.255.255.255', 0)


if __name__ == '__main__':
    unittest.main()
