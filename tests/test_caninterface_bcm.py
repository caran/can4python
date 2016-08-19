#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_caninterface_bcm
----------------------------------

Tests for `caninterface_bcm` module.


Notes:
  A virtual CAN interface 'vcan' must be enabled for this test. See enable_virtual_can_bus().
  Must be run as sudo.

"""
import subprocess
import sys
import time
import unittest

assert sys.version_info >= (3, 4, 0), "Python version 3.4 or later required!"

from can4python import canframe
from can4python import caninterface_bcm
from can4python import exceptions

try:
    from .test_caninterface_raw import VIRTUAL_CAN_BUS_NAME, enable_virtual_can_bus, disable_virtual_can_bus
except SystemError:  # When running this file directly
    from test_caninterface_raw import VIRTUAL_CAN_BUS_NAME, enable_virtual_can_bus, disable_virtual_can_bus


class TestSocketCanBcmInterface(unittest.TestCase):

    # Scaffolding #

    NUMBER_OF_LOOPS = 10000
    FRAME_SENDER_SPACING_MILLISECONDS = 0.1
    FRAME_ID_RECEIVE = 4
    FRAME_ID_SEND = 1
    FRAME_NUMBER_OF_DATABYTES = 8

    NONEXISTING_CAN_BUS_NAME = "vcan8"
    NONEXISTING_FRAME_ID = 22

    def setUp(self):
        enable_virtual_can_bus()
        self.interface = caninterface_bcm.SocketCanBcmInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.simulated_can_process = None

    def tearDown(self):
        self.interface.close()
        try:
            self.simulated_can_process.terminate()
        except (AttributeError, ProcessLookupError) as _:
            pass
        enable_virtual_can_bus()

    def start_can_frame_sender(self, interval_milliseconds=FRAME_SENDER_SPACING_MILLISECONDS):
        """Send CAN frames using the cangen command. Unlimited number of frames."""
        self.simulated_can_process = subprocess.Popen(["cangen", VIRTUAL_CAN_BUS_NAME,
                                                       "-I", str(self.FRAME_ID_RECEIVE),
                                                       "-L", str(self.FRAME_NUMBER_OF_DATABYTES),
                                                       "-D", "i",
                                                       "-g", str(interval_milliseconds)],
                                                      shell=False, stderr=subprocess.STDOUT)
    # Creation etc #

    def testConstructor(self):
        a = caninterface_bcm.SocketCanBcmInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(a.interfacename, VIRTUAL_CAN_BUS_NAME)
        a.close()
        self.assertEqual(a.interfacename, VIRTUAL_CAN_BUS_NAME)
        
        b = caninterface_bcm.SocketCanBcmInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(b.interfacename, VIRTUAL_CAN_BUS_NAME)
        b.close()
        
        c = caninterface_bcm.SocketCanBcmInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(c.interfacename, VIRTUAL_CAN_BUS_NAME)
        c.close()
        
        d = caninterface_bcm.SocketCanBcmInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(d.interfacename, VIRTUAL_CAN_BUS_NAME)
        d.close()

    def testConstructorWrongValue(self):
        self.assertRaises(exceptions.CanException, caninterface_bcm.SocketCanBcmInterface, VIRTUAL_CAN_BUS_NAME, -1)
        self.assertRaises(exceptions.CanException, caninterface_bcm.SocketCanBcmInterface, VIRTUAL_CAN_BUS_NAME, -1.0)

    def testConstructorWrongType(self):
        self.assertRaises(exceptions.CanException, caninterface_bcm.SocketCanBcmInterface, VIRTUAL_CAN_BUS_NAME, "ABC")

    def testConstructorSeveralInterfaces(self):
        a = caninterface_bcm.SocketCanBcmInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(a.interfacename, VIRTUAL_CAN_BUS_NAME)
        
        b = caninterface_bcm.SocketCanBcmInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(b.interfacename, VIRTUAL_CAN_BUS_NAME)
        
        c = caninterface_bcm.SocketCanBcmInterface(VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(c.interfacename, VIRTUAL_CAN_BUS_NAME)
        
        a.close()
        b.close()
        c.close()

    def testCreateNonExistingBus(self):
        self.assertRaises(exceptions.CanException,
                          caninterface_bcm.SocketCanBcmInterface,
                          self.NONEXISTING_CAN_BUS_NAME, timeout=1.0)
        self.assertRaises(exceptions.CanException, caninterface_bcm.SocketCanBcmInterface, 1, 1.0)

    def testWriteToInterfacenameAttribute(self):
        self.assertRaises(AttributeError, setattr, self.interface, 'interfacename', 'can0')

    def testRepr(self):
        result = repr(self.interface)
        known_result = "SocketCan BCM interface: {}".format(VIRTUAL_CAN_BUS_NAME.strip())
        self.assertEqual(result.strip(), known_result.strip())

    # Receive #

    def testSetupReception(self):
        self.interface.setup_reception(self.FRAME_ID_RECEIVE)
        self.interface.setup_reception(self.FRAME_ID_RECEIVE, min_interval=None)
        self.interface.setup_reception(self.FRAME_ID_RECEIVE, min_interval=0)  # 0 and None should be the same

    def testSetupReceptionWrongValue(self):
        self.assertRaises(exceptions.CanException, self.interface.setup_reception, -1)
        self.assertRaises(exceptions.CanException, self.interface.setup_reception, 0x007, "ABC")
        self.assertRaises(exceptions.CanException, self.interface.setup_reception, 0x007, 'standard', -1.0)
        self.assertRaises(exceptions.CanException, self.interface.setup_reception, 0x007, 'standard', 0.05, b"\x00")
        self.assertRaises(exceptions.CanException, self.interface.setup_reception, 0x007, 'standard', 0.05, "ABC")

    def testSetupReceptionWrongType(self):
        self.assertRaises(exceptions.CanException, self.interface.setup_reception, "ABC")
        self.assertRaises(exceptions.CanException, self.interface.setup_reception, 0x007, 1)
        self.assertRaises(TypeError, self.interface.setup_reception, 0x007, 'standard', "ABC")
        self.assertRaises(TypeError, self.interface.setup_reception, 0x007, 'standard', 0.05, 1)

    def testReceiveData(self):
        self.start_can_frame_sender()
        self.interface.setup_reception(self.FRAME_ID_RECEIVE)
        received_frame = self.interface.recv_next_frame()
        self.assertEqual(len(received_frame), self.FRAME_NUMBER_OF_DATABYTES)

    def testReceiveStoppedReception(self):
        self.start_can_frame_sender()
        self.interface.setup_reception(self.FRAME_ID_RECEIVE)
        self.interface.stop_reception(self.FRAME_ID_RECEIVE)
        self.assertRaises(exceptions.CanTimeoutException, self.interface.recv_next_frame)

    def testReceiveWrongId(self):
        self.start_can_frame_sender()
        self.interface.setup_reception(self.NONEXISTING_FRAME_ID)
        self.assertRaises(exceptions.CanTimeoutException, self.interface.recv_next_frame)

    def testReceiveSpeed(self):
        self.start_can_frame_sender()

        self.interface.setup_reception(self.FRAME_ID_RECEIVE)
        time.sleep(0.1)

        starttime = time.time()
        for i in range(self.NUMBER_OF_LOOPS):
            self.interface.recv_next_frame()
        execution_time = time.time() - starttime

        time_per_loop_ms = 1000 * execution_time / self.NUMBER_OF_LOOPS
        outputstring = "\n --> Received {} frames in {:.1f} s ({:.1f} ms per frame). Frame sender spacing {:.1f} ms.\n".\
            format(self.NUMBER_OF_LOOPS, execution_time, time_per_loop_ms, self.FRAME_SENDER_SPACING_MILLISECONDS)
        print(outputstring)

    def testReceiveSpeedThrottled(self):
        THROTTLE_INTERVAL_MILLISECONDS = 20  
        THROTTLE_LOOPS = 100
        ALLOWED_RELATIVE_ERROR = 0.1
        nominal_time = THROTTLE_INTERVAL_MILLISECONDS * THROTTLE_LOOPS / 1000  # seconds

        self.start_can_frame_sender()
        self.interface.setup_reception(self.FRAME_ID_RECEIVE, min_interval=THROTTLE_INTERVAL_MILLISECONDS)
        time.sleep(0.1)

        starttime = time.time()
        for i in range(THROTTLE_LOOPS):
            self.interface.recv_next_frame()
        execution_time = time.time() - starttime
        self.assertLess(abs(execution_time - nominal_time), ALLOWED_RELATIVE_ERROR * nominal_time)

    def testReceiveDataChanged(self):
        """Verify that data change filtering works, by measuring time to receive a small number of frames from a larger data flow."""
        SENDER_INTERVAL_MILLISECONDS = 1
        DATA_CHANGED_LOOPS = 20
        DATA_MASK = b"\x80\x00\x00\x00\x00\x00\x00\x00"  # One frame out of 128
        ALLOWED_RELATIVE_ERROR = 2.0
        nominal_time = SENDER_INTERVAL_MILLISECONDS * 128 * DATA_CHANGED_LOOPS / 1000  # seconds

        self.start_can_frame_sender(SENDER_INTERVAL_MILLISECONDS)
        self.interface.setup_reception(self.FRAME_ID_RECEIVE, data_mask=DATA_MASK)
        time.sleep(0.1)

        starttime = time.time()
        for i in range(DATA_CHANGED_LOOPS):
            self.interface.recv_next_frame()
        execution_time = time.time() - starttime
        
        allowed_error = ALLOWED_RELATIVE_ERROR * nominal_time
        time_error = abs(execution_time - nominal_time)
        outputstring = "\n --> Received {} frames in {:.1f} s, nominal time {:.1f} s. Error {:.1f} s (allowed {:.1f} s).\n".\
            format(DATA_CHANGED_LOOPS, execution_time, nominal_time, time_error, allowed_error)
        print(outputstring)
        self.assertLess(time_error, allowed_error)

    def testReceiveDataChangedShorterDlcThanMask(self):
        """Verify that filtering works also when the input frame is shorter (3 bytes) than the data mask (8 bytes)."""
        SENDER_INTERVAL_MILLISECONDS = 1
        DATA_CHANGED_LOOPS = 20
        DATA_MASK = b"\x80\x00\x00\x00\x00\x00\x00\x00"  # One frame out of 128
        ALLOWED_RELATIVE_ERROR = 2.0
        nominal_time = SENDER_INTERVAL_MILLISECONDS * DATA_CHANGED_LOOPS * 128 / 1000

        self.interface.setup_reception(self.FRAME_ID_RECEIVE, data_mask=DATA_MASK)
        time.sleep(0.1)

        self.simulated_can_process = subprocess.Popen(["cangen", VIRTUAL_CAN_BUS_NAME,
                                                       "-I", str(self.FRAME_ID_RECEIVE),
                                                       "-L", "3",
                                                       "-D", "i",
                                                       "-g", str(SENDER_INTERVAL_MILLISECONDS)],
                                                      shell=False, stderr=subprocess.STDOUT)
        starttime = time.time()
        for i in range(DATA_CHANGED_LOOPS):
            self.interface.recv_next_frame()
        execution_time = time.time() - starttime

        allowed_error = ALLOWED_RELATIVE_ERROR * nominal_time
        time_error = abs(execution_time - nominal_time)
        outputstring = "\n --> Received {} frames in {:.1f} s, nominal time {:.1f} s. Error {:.1f} s (allowed {:.1f} s).\n".\
            format(DATA_CHANGED_LOOPS, execution_time, nominal_time, time_error, allowed_error)
        print(outputstring)
        self.assertLess(time_error, allowed_error)

    def testReceiveDlcChanged(self):
        """Verify that we are receiving frames where each frame is longer (or no data) than the previous."""
        SENDER_INTERVAL_MILLISECONDS = 1
        NUMBER_OF_DLC_FRAMES = 30
        DATA_MASK = b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Do not look at data changes
        self.interface.setup_reception(self.FRAME_ID_RECEIVE, data_mask=DATA_MASK)
        self.simulated_can_process = subprocess.Popen(["cangen", VIRTUAL_CAN_BUS_NAME,
                                                       "-I", str(self.FRAME_ID_RECEIVE),
                                                       "-L", "i",
                                                       "-D", "0102030405060708",
                                                       "-n", str(NUMBER_OF_DLC_FRAMES),
                                                       "-g", str(SENDER_INTERVAL_MILLISECONDS)],
                                                      shell=False, stderr=subprocess.STDOUT)
        number_of_received_frames = 0
        while True:
            try:
                self.interface.recv_next_frame()
                number_of_received_frames += 1
            except exceptions.CanTimeoutException:
                break
        self.assertEqual(number_of_received_frames, NUMBER_OF_DLC_FRAMES)

    def testReceiveNoData(self):
        self.assertRaises(exceptions.CanTimeoutException, self.interface.recv_next_frame)

    def testReceiveClosedBus(self):
        disable_virtual_can_bus()
        self.assertRaises(exceptions.CanException, self.interface.recv_next_frame)

    def testReceiveClosedInterface(self):
        self.interface.close()
        self.assertRaises(exceptions.CanException, self.interface.recv_next_frame)

    # Send #

    def testSendSingleFrameWrongType(self):
        self.assertRaises(exceptions.CanException, self.interface.send_frame, 1)
        self.assertRaises(exceptions.CanException, self.interface.send_frame, "ABC")

    def testSendSingleFrame(self):
        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME, '-n', '1'], shell=False,
                                                      universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.1)
        frame = canframe.CanFrame.from_empty_bytes(self.FRAME_ID_SEND, self.FRAME_NUMBER_OF_DATABYTES)
        self.interface.send_frame(frame)

        print("\nWaiting for a subprocess to receive a single CAN frame, sent via 'send_frame'.")
        out, err = self.simulated_can_process.communicate()
        print("Confirmed CAN frame.")

        known_result = "[8]  00 00 00 00 00 00 00 00"
        self.assertIn(known_result, out)

    def testSetupPeriodicSendWrongValue(self):
        frame_zeros = canframe.CanFrame(self.FRAME_ID_SEND, b'\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertRaises(exceptions.CanException, self.interface.setup_periodic_send, frame_zeros, -1)

    def testSetupPeriodicSendWrongType(self):
        frame_zeros = canframe.CanFrame(self.FRAME_ID_SEND, b'\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertRaises(exceptions.CanException, self.interface.setup_periodic_send, 1)
        self.assertRaises(exceptions.CanException, self.interface.setup_periodic_send, frame_zeros, "ABC")

    def testSetupPeriodicSendWrongType(self):
        frame_zeros = canframe.CanFrame(self.FRAME_ID_SEND, b'\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertRaises(exceptions.CanException, self.interface.setup_periodic_send, 1)
        self.assertRaises(exceptions.CanException, self.interface.setup_periodic_send, frame_zeros, "ABC")

    def testSendPeriodicAndChangeFrameAndStop(self):
        """Start periodic CAN transmission, update frame data (not interval), and finally stop transmission."""
        RESULT_ALLOWED_DIFFERENCE = 5 # Number of missed frames, or when stopping sending too late.
        TRANSMISSION_INTERVAL_MILLISECONDS = 20
        MEASUREMENT_TIME = 1  # seconds

        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME], shell=False,
                                                      universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.1)
        frame_zeros = canframe.CanFrame(self.FRAME_ID_SEND, b'\x00\x00\x00\x00\x00\x00\x00\x00')
        frame_ones = canframe.CanFrame(self.FRAME_ID_SEND, b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

        print("\nSetting up periodic CAN frame transmission.")
        self.interface.setup_periodic_send(frame_zeros, TRANSMISSION_INTERVAL_MILLISECONDS)
        time.sleep(MEASUREMENT_TIME)

        self.interface.setup_periodic_send(frame_ones, restart_timer=False)
        time.sleep(MEASUREMENT_TIME)

        self.interface.stop_periodic_send(self.FRAME_ID_SEND)
        time.sleep(MEASUREMENT_TIME)

        self.simulated_can_process.terminate()
        out, err = self.simulated_can_process.communicate()
        print("Periodic CAN frame transmission done.")

        projected_number_of_frames = MEASUREMENT_TIME * 1000 / TRANSMISSION_INTERVAL_MILLISECONDS
        number_of_frames_zeros = out.count(" {:03.0f}   [8]  00 00 00 00 00 00 00 00".format(self.FRAME_ID_SEND))
        self.assertGreaterEqual(number_of_frames_zeros, projected_number_of_frames - RESULT_ALLOWED_DIFFERENCE)
        self.assertLessEqual(number_of_frames_zeros, projected_number_of_frames + RESULT_ALLOWED_DIFFERENCE)

        number_of_frames_ones = out.count(" {:03.0f}   [8]  FF FF FF FF FF FF FF FF".format(self.FRAME_ID_SEND))
        self.assertGreaterEqual(number_of_frames_ones, projected_number_of_frames - RESULT_ALLOWED_DIFFERENCE)
        self.assertLessEqual(number_of_frames_ones, projected_number_of_frames + RESULT_ALLOWED_DIFFERENCE)

    def testSendPeriodicAndChangeFrameAndStopExtended(self):
        """Start periodic CAN transmission, update frame data (not interval), and finally stop transmission."""
        RESULT_ALLOWED_DIFFERENCE = 5 # Number of missed frames, or when stopping sending too late.
        TRANSMISSION_INTERVAL_MILLISECONDS = 20
        MEASUREMENT_TIME = 1  # seconds

        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME], shell=False,
                                                      universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.1)

        frame_zeros = canframe.CanFrame(self.FRAME_ID_SEND, b'\x00\x00\x00\x00\x00\x00\x00\x00', 'extended')
        frame_ones = canframe.CanFrame(self.FRAME_ID_SEND, b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF', 'extended')

        self.interface.setup_periodic_send(frame_zeros, TRANSMISSION_INTERVAL_MILLISECONDS)
        time.sleep(MEASUREMENT_TIME)

        self.interface.setup_periodic_send(frame_ones, restart_timer=False)
        time.sleep(MEASUREMENT_TIME)

        self.interface.stop_periodic_send(self.FRAME_ID_SEND, 'extended')
        time.sleep(MEASUREMENT_TIME)

        self.simulated_can_process.terminate()
        out, err = self.simulated_can_process.communicate()

        projected_number_of_frames = MEASUREMENT_TIME * 1000 / TRANSMISSION_INTERVAL_MILLISECONDS

        number_of_frames_zeros = out.count(" {:08.0f}   [8]  00 00 00 00 00 00 00 00".format(self.FRAME_ID_SEND))
        self.assertGreaterEqual(number_of_frames_zeros, projected_number_of_frames - RESULT_ALLOWED_DIFFERENCE)
        self.assertLessEqual(number_of_frames_zeros, projected_number_of_frames + RESULT_ALLOWED_DIFFERENCE)

        number_of_frames_ones = out.count(" {:08.0f}   [8]  FF FF FF FF FF FF FF FF".format(self.FRAME_ID_SEND))
        self.assertGreaterEqual(number_of_frames_ones, projected_number_of_frames - RESULT_ALLOWED_DIFFERENCE)
        self.assertLessEqual(number_of_frames_ones, projected_number_of_frames + RESULT_ALLOWED_DIFFERENCE)

    def testStopNonexistingPeriodicTask(self):
        self.assertRaises(exceptions.CanException, self.interface.stop_periodic_send, self.FRAME_ID_SEND)

        TRANSMISSION_INTERVAL_MILLISECONDS = 20
        frame_zeros = canframe.CanFrame(self.FRAME_ID_SEND, b'\x00\x00\x00\x00\x00\x00\x00\x00', 'standard')
        self.interface.setup_periodic_send(frame_zeros, TRANSMISSION_INTERVAL_MILLISECONDS)
        self.assertRaises(exceptions.CanException, self.interface.stop_periodic_send, self.FRAME_ID_SEND, 'extended')

    def testSendClosedBus(self):
        disable_virtual_can_bus()
        frame = canframe.CanFrame.from_empty_bytes(self.FRAME_ID_SEND, self.FRAME_NUMBER_OF_DATABYTES)
        self.assertRaises(exceptions.CanException, self.interface.send_frame, frame)

    def testSendClosedInterface(self):
        frame = canframe.CanFrame.from_empty_bytes(self.FRAME_ID_SEND, self.FRAME_NUMBER_OF_DATABYTES)
        self.interface.close()
        self.assertRaises(exceptions.CanException, self.interface.send_frame, frame)


if __name__ == '__main__': 
    
        # Run all tests #
    unittest.main()
    
        # Run a single test #
    # suite = unittest.TestSuite()
    # suite.addTest(TestSocketCanBcmInterface("testReceiveDlcChanged"))
    # unittest.TextTestRunner(verbosity=2).run(suite)
