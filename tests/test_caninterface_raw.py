#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_caninterface_raw
----------------------------------

Tests for `caninterface_raw` module.


Notes:
  A virtual CAN interface 'vcan' must be enabled for this test. See enable_virtual_can_bus().
  Must be run as sudo.

"""

import subprocess
import sys
import time
import unittest

assert sys.version_info >= (3, 3, 0), "Python version 3.3 or later required!"

from can4python import exceptions
from can4python import canframe
from can4python import caninterface_raw

VIRTUAL_CAN_BUS_NAME = "vcan0"


def enable_virtual_can_bus():
    try:
        subprocess.check_output(["modprobe", "vcan"])
    except:
        raise exceptions.CanException("Could not modprobe vcan. Are you sure you are running as sudo?")
    try:
        subprocess.check_output(["ip", "link", "add", "dev", VIRTUAL_CAN_BUS_NAME,
                                 "type", "vcan"], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        pass
    try:
        subprocess.check_output(["ifconfig", VIRTUAL_CAN_BUS_NAME, "up"])
    except subprocess.CalledProcessError:
        raise exceptions.CanException("Could not enable {}. Are you sure you are running as sudo?".format(
            VIRTUAL_CAN_BUS_NAME))


def disable_virtual_can_bus():
    subprocess.check_output(["ifconfig", VIRTUAL_CAN_BUS_NAME, "down"])


class TestSocketCanRawInterface(unittest.TestCase):

    # Scaffolding #

    NUMBER_OF_LOOPS = 10000
    FRAME_SENDER_SPACING_MILLISECONDS = 0.1
    FRAME_ID_RECEIVE = 4
    FRAME_ID_SEND = 1
    FRAME_NUMBER_OF_DATABYTES = 8

    NONEXISTING_CAN_BUS_NAME = "vcan8"

    def setUp(self):
        enable_virtual_can_bus()
        self.interface = caninterface_raw.SocketCanRawInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.simulated_can_process = None

    def tearDown(self):
        self.interface.close()
        try:
            self.simulated_can_process.terminate()
        except (AttributeError, ProcessLookupError) as _:
            pass
        enable_virtual_can_bus()

    def start_can_frame_sender(self):
        """Send CAN frames using the cangen command."""
        self.simulated_can_process = subprocess.Popen(["cangen", VIRTUAL_CAN_BUS_NAME,
                                                       "-I", str(self.FRAME_ID_RECEIVE),
                                                       "-L", str(self.FRAME_NUMBER_OF_DATABYTES),
                                                       "-D", "i",
                                                       "-g", str(self.FRAME_SENDER_SPACING_MILLISECONDS)],
                                                      shell=False, stderr=subprocess.STDOUT)
    # Creation etc #

    def testConstructor(self):
        a = caninterface_raw.SocketCanRawInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(a.interfacename, VIRTUAL_CAN_BUS_NAME)
        a.close()
        self.assertEqual(a.interfacename, VIRTUAL_CAN_BUS_NAME)
        
        b = caninterface_raw.SocketCanRawInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(b.interfacename, VIRTUAL_CAN_BUS_NAME)
        b.close()
        
        c = caninterface_raw.SocketCanRawInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(c.interfacename, VIRTUAL_CAN_BUS_NAME)
        c.close()
        
        d = caninterface_raw.SocketCanRawInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(d.interfacename, VIRTUAL_CAN_BUS_NAME)
        d.close()

    def testConstructorWrongValue(self):
        self.assertRaises(exceptions.CanException, caninterface_raw.SocketCanRawInterface, VIRTUAL_CAN_BUS_NAME, -1)
        self.assertRaises(exceptions.CanException, caninterface_raw.SocketCanRawInterface, VIRTUAL_CAN_BUS_NAME, -1.0)

    def testConstructorWrongType(self):
        self.assertRaises(exceptions.CanException, caninterface_raw.SocketCanRawInterface, 1, 1.0)
        self.assertRaises(exceptions.CanException, caninterface_raw.SocketCanRawInterface, VIRTUAL_CAN_BUS_NAME, "ABC")

    def testConstructorSeveralInterfaces(self):
        a = caninterface_raw.SocketCanRawInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(a.interfacename, VIRTUAL_CAN_BUS_NAME)
        
        b = caninterface_raw.SocketCanRawInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(b.interfacename, VIRTUAL_CAN_BUS_NAME)
        
        c = caninterface_raw.SocketCanRawInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(c.interfacename, VIRTUAL_CAN_BUS_NAME)
        
        a.close()
        b.close()
        c.close()

    def testCreateNonExistingBus(self):
        self.assertRaises(exceptions.CanException, caninterface_raw.SocketCanRawInterface, self.NONEXISTING_CAN_BUS_NAME)

    def testWriteToInterfacenameAttribute(self):
        self.assertRaises(AttributeError, setattr, self.interface, 'interfacename', 'can0')

    def testRepr(self):
        result = repr(self.interface)
        known_result = "SocketCan raw interface: {}".format(VIRTUAL_CAN_BUS_NAME.strip())
        self.assertEqual(result.strip(), known_result.strip())

    # Receive #

    def testReceiveData(self):
        self.start_can_frame_sender()

        received_frame = self.interface.recv_next_frame()
        self.assertEqual(len(received_frame.frame_data), self.FRAME_NUMBER_OF_DATABYTES)

    def testReceiveSpeed(self):
        self.start_can_frame_sender()

        starttime = time.time()
        for i in range(self.NUMBER_OF_LOOPS):
            self.interface.recv_next_frame()
        execution_time = time.time() - starttime

        time_per_loop_ms = 1000 * execution_time / self.NUMBER_OF_LOOPS
        outputstring = "\n\n --> Received {} frames in {:.1f} s ({:.1f} ms per frame). Frame sender spacing {:.1f} ms.\n".\
            format(self.NUMBER_OF_LOOPS, execution_time, time_per_loop_ms, self.FRAME_SENDER_SPACING_MILLISECONDS)
        print(outputstring)

    def testReceiveNoData(self):
        self.assertRaises(exceptions.CanTimeoutException, self.interface.recv_next_frame)

    def testReceiveClosedBus(self):
        disable_virtual_can_bus()
        self.assertRaises(exceptions.CanException, self.interface.recv_next_frame)

    def testReceiveClosedInterface(self):
        self.interface.close()
        self.assertRaises(exceptions.CanException, self.interface.recv_next_frame)

    # Send #

    def testSend(self):

        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME, '-n', '1'], shell=False,
                                                      universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.1)
        frame = canframe.CanFrame.from_empty_bytes(self.FRAME_ID_SEND, self.FRAME_NUMBER_OF_DATABYTES)
        self.interface.send_frame(frame)

        print("\nWaiting for testfile to send_frame CAN frame ")
        out, err = self.simulated_can_process.communicate()
        print("Confirmed CAN frame")

        known_result = "[8]  00 00 00 00 00 00 00 00"
        self.assertIn(known_result, out)

    def testSendClosedBus(self):
        disable_virtual_can_bus()
        frame = canframe.CanFrame.from_empty_bytes(self.FRAME_ID_SEND, self.FRAME_NUMBER_OF_DATABYTES)
        self.assertRaises(exceptions.CanException, self.interface.send_frame, frame)

    def testSendClosedInterface(self):
        frame = canframe.CanFrame.from_empty_bytes(self.FRAME_ID_SEND, self.FRAME_NUMBER_OF_DATABYTES)
        self.interface.close()
        self.assertRaises(exceptions.CanException, self.interface.send_frame, frame)

    # Set filters #

    def testTooFewTooManyFiltersDefined(self):
        # Will skip setting any filters.
        self.interface.set_receive_filters([])
        self.interface.set_receive_filters(list(range(200)))

if __name__ == '__main__': 
    
        # Run all tests #
    unittest.main()
    
        # Run a single test #
    # suite = unittest.TestSuite()
    # suite.addTest(TestSocketCanInterfaceRaw("testConstructor"))
    # unittest.TextTestRunner(verbosity=2).run(suite)
