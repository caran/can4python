#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_canbus
----------------------------------

Tests for `canbus` module.


Notes:
  A virtual CAN interface 'vcan' must be enabled for this test.
  Must be run as sudo.


"""
import contextlib
import copy
import os.path
import subprocess
import sys
import time
import unittest

assert sys.version_info >= (3, 3, 0), "Python version 3.3 or later required!"

from can4python import exceptions
from can4python import canbus
from can4python import canframe
from can4python import configuration

try:
    from .test_caninterface_raw import VIRTUAL_CAN_BUS_NAME, enable_virtual_can_bus
except SystemError:  # When running this file directly
    from test_caninterface_raw import VIRTUAL_CAN_BUS_NAME, enable_virtual_can_bus

try:
    from .test_configuration import FRAME_ID_SEND, FRAME_ID_RECEIVE, TESTCONFIG1
except SystemError:
    from test_configuration import FRAME_ID_SEND, FRAME_ID_RECEIVE, TESTCONFIG1

try:
    from .test_filehandler_kcd import INPUT_FILENAME, INPUT_FILENAME_NO_BUSDEFINITION
except SystemError:
    from test_filehandler_kcd import INPUT_FILENAME, INPUT_FILENAME_NO_BUSDEFINITION


class TestCanBus(unittest.TestCase):

    # Scaffolding #

    NUMBER_OF_LOOPS = 1000
    #FRAME_SENDER_SPACING_MILLISECONDS = 0.14  # Approx 90 % busload at 500 kbit/s  Beaglebone is too slow for this
    FRAME_SENDER_SPACING_MILLISECONDS = 1
    FRAME_NUMBER_OF_DATABYTES = 8

    OUTPUT_FILENAME_4 = "test_out_4_TEMPORARY.kcd"
    OUTPUT_FILENAME_5 = "test_out_5_TEMPORARY.kcd"
    OUTPUT_FILENAME_6 = "test_out_6_TEMPORARY.kcd"
    OUTPUT_FILENAME_7 = "test_out_7_TEMPORARY.kcd"

    def setUp(self):
        enable_virtual_can_bus()
        self.canbus_raw = canbus.CanBus(copy.deepcopy(TESTCONFIG1), VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.canbus_bcm = canbus.CanBus(copy.deepcopy(TESTCONFIG1), VIRTUAL_CAN_BUS_NAME, timeout=1.0, use_bcm=True)

        parent_directory = os.path.dirname(__file__)
        self.input_filename = os.path.join(parent_directory, INPUT_FILENAME)
        self.input_filename_no_busdefinition = os.path.join(parent_directory, INPUT_FILENAME_NO_BUSDEFINITION)

        self.simulated_can_process = None

    def tearDown(self):
        self.canbus_raw.caninterface.close()
        self.canbus_bcm.caninterface.close()
        try:
            self.simulated_can_process.terminate()
        except (AttributeError, ProcessLookupError) as _:
            pass

        for filename in [self.OUTPUT_FILENAME_4,
                         self.OUTPUT_FILENAME_5,
                         self.OUTPUT_FILENAME_6,
                         self.OUTPUT_FILENAME_7]:
            with contextlib.suppress(FileNotFoundError):
                os.remove(filename)


    # Constructor #

    def testUseBcmAttribute(self):
        self.assertFalse(self.canbus_raw.use_bcm)
        self.assertTrue(self.canbus_bcm.use_bcm)

    def testWriteToBcmAttribute(self):
        self.assertRaises(AttributeError, setattr, self.canbus_raw, 'use_bcm', True)
        self.assertRaises(AttributeError, setattr, self.canbus_raw, 'use_bcm', False)
        self.assertRaises(AttributeError, setattr, self.canbus_bcm, 'use_bcm', True)
        self.assertRaises(AttributeError, setattr, self.canbus_bcm, 'use_bcm', False)

    def testWriteToConfigAttribute(self):
        self.assertRaises(AttributeError, setattr, self.canbus_raw, 'config', configuration.Configuration())
        self.assertRaises(AttributeError, setattr, self.canbus_bcm, 'config', configuration.Configuration())

    def testConstructor(self):
        self.canbus_raw.caninterface.close()

        config = configuration.Configuration()
        a = canbus.CanBus(config, VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(a.caninterface.interfacename, VIRTUAL_CAN_BUS_NAME)
        a.caninterface.close()
        self.assertEqual(a.caninterface.interfacename, VIRTUAL_CAN_BUS_NAME)
        self.assertFalse(a.use_bcm)

        b = canbus.CanBus(config, VIRTUAL_CAN_BUS_NAME, timeout=1.0)
        self.assertEqual(b.caninterface.interfacename, VIRTUAL_CAN_BUS_NAME)
        self.assertFalse(a.use_bcm)
        b.caninterface.close()
        self.assertEqual(b.caninterface.interfacename, VIRTUAL_CAN_BUS_NAME)

        c = canbus.CanBus(config, VIRTUAL_CAN_BUS_NAME, timeout=1.0, use_bcm=True)
        self.assertEqual(c.caninterface.interfacename, VIRTUAL_CAN_BUS_NAME)
        self.assertFalse(a.use_bcm)
        c.caninterface.close()
        self.assertEqual(c.caninterface.interfacename, VIRTUAL_CAN_BUS_NAME)

    def testReadConfigFromFile(self):
        """See test_configuration.py and others for more complete configuration read testing"""
        bus = canbus.CanBus.from_kcd_file(self.input_filename, VIRTUAL_CAN_BUS_NAME)
        self.assertFalse(bus.use_bcm)

        self.assertEqual(bus.caninterface.interfacename, VIRTUAL_CAN_BUS_NAME)
        self.assertEqual(bus.config.busname, "Mainbus")

        self.assertEqual(bus.config.framedefinitions[1].frame_id, 1)
        self.assertEqual(bus.config.framedefinitions[1].frame_id, 1)
        self.assertEqual(bus.config.framedefinitions[1].name, 'testframedef1')

        bus2 = canbus.CanBus.from_kcd_file(self.input_filename, VIRTUAL_CAN_BUS_NAME, use_bcm=True)
        self.assertEqual(bus2.caninterface.interfacename, VIRTUAL_CAN_BUS_NAME)
        self.assertEqual(bus2.config.busname, "Mainbus")

    def testRepr(self):
        result = repr(self.canbus_raw)
        known_result = "CAN bus 'bus1' on CAN interface: {}, having 2 frameIDs defined. Protocol RAW".format(
            VIRTUAL_CAN_BUS_NAME.strip())
        self.assertEqual(result.strip(), known_result.strip())

    def testGetDescriptiveAsciiArt(self):
        result = self.canbus_raw.get_descriptive_ascii_art()
        print('\n\n' + result)  # Check the output manually


    # Send signals #

    def testSendRaw(self):
        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME,
                                                       '-n', '1'],
                                                      shell=False, universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        signalvalues_to_send = {'testsignal1': 1,
                                'testsignal2': 256 * 2 + 3,
                                'testsignal3': 256 * 4 + 5}
        time.sleep(0.1)
        self.canbus_raw.send_signals(signalvalues_to_send)

        out, err = self.simulated_can_process.communicate(timeout=2)
        known_result = "[8]  02 03 00 05 04 00 00 01"
        self.assertIn(known_result, out)

    def testSendRawKeywordArguments(self):
        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME,
                                                       '-n', '1'],
                                                      shell=False, universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.1)
        self.canbus_raw.send_signals(testsignal1=1, testsignal2=256*2+7, testsignal3=256*4+5)

        out, err = self.simulated_can_process.communicate(timeout=2)
        known_result = "[8]  02 07 00 05 04 00 00 01"
        self.assertIn(known_result, out)

    def testSendBcm(self):
        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME,
                                                       '-n', '1'],
                                                      shell=False, universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        signalvalues_to_send = {'testsignal1': 1,
                                'testsignal2': 256 * 2 + 3,
                                'testsignal3': 256 * 4 + 5}
        time.sleep(0.1)
        self.canbus_bcm.send_signals(signalvalues_to_send)

        out, err = self.simulated_can_process.communicate(timeout=2)
        known_result = "[8]  02 03 00 05 04 00 00 01"
        self.assertIn(known_result, out)

    def testSendBcmFrame(self):
        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME,
                                                       '-n', '1'],
                                                      shell=False, universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.1)
        frame_to_send = canframe.CanFrame(FRAME_ID_SEND, b"\x02\x03\x00\x05\x04\x00\x00\x01")
        self.canbus_bcm.send_frame(frame_to_send)

        out, err = self.simulated_can_process.communicate(timeout=2)
        known_result = "[8]  02 03 00 05 04 00 00 01"
        self.assertIn(known_result, out)

    def testSendSpeedAndDetectAllRaw(self):

        NUMBER_OF_FRAMES_TO_SEND = 1000  # Seems to give problems for larger values

        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME,
                                                       "-n", str(NUMBER_OF_FRAMES_TO_SEND)],
                                                      shell=False, universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.1)

        starttime = time.time()
        for i in range(NUMBER_OF_FRAMES_TO_SEND):
            signalvalues_to_send = {'testsignal1': 1,
                                    'testsignal2': i,
                                    'testsignal3': 256 * 4 + 5}
            self.canbus_raw.send_signals(signalvalues_to_send)

        try:
            self.simulated_can_process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            raise exceptions.CanTimeoutException("At least one of the {} sent frames was not seen by candump.".format(
                NUMBER_OF_FRAMES_TO_SEND))
        execution_time = time.time() - starttime

        time_per_loop_ms = 1000 * execution_time / NUMBER_OF_FRAMES_TO_SEND
        frames_per_seconds = NUMBER_OF_FRAMES_TO_SEND / execution_time
        output_string = "\n --> Sent {} frames in {:.1f} s ({:.2f} ms per frame, {:.1f} frames/s). ".format(
            NUMBER_OF_FRAMES_TO_SEND, execution_time, time_per_loop_ms, frames_per_seconds)
        print(output_string)

    def testSendSpeedAndDetectAllBcm(self):

        NUMBER_OF_FRAMES_TO_SEND = 1000  # Seems to give problems for larger values

        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME,
                                                       "-n", str(NUMBER_OF_FRAMES_TO_SEND)],
                                                      shell=False, universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.1)

        starttime = time.time()
        for i in range(NUMBER_OF_FRAMES_TO_SEND):
            signalvalues_to_send = {'testsignal1': 1,
                                    'testsignal2': i,
                                    'testsignal3': 256 * 4 + 5}
            self.canbus_bcm.send_signals(signalvalues_to_send)

        try:
            self.simulated_can_process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            raise exceptions.CanTimeoutException("At least one of the {} sent frames was not seen by candump.".format(
                NUMBER_OF_FRAMES_TO_SEND))
        execution_time = time.time() - starttime

        time_per_loop_ms = 1000 * execution_time / NUMBER_OF_FRAMES_TO_SEND
        frames_per_seconds = NUMBER_OF_FRAMES_TO_SEND / execution_time
        output_string = "\n --> Sent {} frames in {:.1f} s ({:.2f} ms per frame, {:.1f} frames/s). ".format(
            NUMBER_OF_FRAMES_TO_SEND, execution_time, time_per_loop_ms, frames_per_seconds)
        print(output_string)

    def testPeriodicSendingUpdateSignalsAndStop(self):
        RESULT_ALLOWED_DIFFERENCE = 3 # Number of missed frames, or when stopping sending too late.
        TRANSMISSION_INTERVAL_MILLISECONDS = 20
        MEASUREMENT_TIME = 0.5  # seconds

        config = copy.deepcopy(TESTCONFIG1)
        config.framedefinitions[FRAME_ID_SEND].cycletime = TRANSMISSION_INTERVAL_MILLISECONDS
        self.canbus_bcm = canbus.CanBus(config, VIRTUAL_CAN_BUS_NAME, timeout=1.0, use_bcm=True)

        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME], shell=False,
                                                      universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.1)
        signalvalues_to_send = {'testsignal1': 1,
                                'testsignal2': 1,
                                'testsignal3': 256 * 4 + 5}
        self.canbus_bcm.send_signals(signalvalues_to_send)
        time.sleep(MEASUREMENT_TIME)

        signalvalues_to_send = {'testsignal1': 1,
                                'testsignal2': 255,
                                'testsignal3': 256 * 4 + 5}
        self.canbus_bcm.send_signals(signalvalues_to_send)
        time.sleep(MEASUREMENT_TIME)

        self.canbus_bcm.stop_sending()
        time.sleep(MEASUREMENT_TIME)

        self.simulated_can_process.terminate()
        out, err = self.simulated_can_process.communicate()

        projected_number_of_frames = MEASUREMENT_TIME * 1000 / TRANSMISSION_INTERVAL_MILLISECONDS
        number_of_frames_A = out.count(" {:03.0f}   [8]  00 01 00 05 04 00 00 01".format(FRAME_ID_SEND))
        self.assertGreaterEqual(number_of_frames_A, projected_number_of_frames - RESULT_ALLOWED_DIFFERENCE)
        self.assertLessEqual(number_of_frames_A, projected_number_of_frames + RESULT_ALLOWED_DIFFERENCE)

        number_of_frames_B = out.count(" {:03.0f}   [8]  00 FF 00 05 04 00 00 01".format(FRAME_ID_SEND))
        self.assertGreaterEqual(number_of_frames_B, projected_number_of_frames - RESULT_ALLOWED_DIFFERENCE)
        self.assertLessEqual(number_of_frames_B, projected_number_of_frames + RESULT_ALLOWED_DIFFERENCE)

    def testStartSendingAllSignals(self):
        RESULT_ALLOWED_DIFFERENCE = 3 # Number of missed frames, or when stopping sending too late.
        TRANSMISSION_INTERVAL_MILLISECONDS = 20
        MEASUREMENT_TIME = 0.5  # seconds

        config = copy.deepcopy(TESTCONFIG1)
        config.framedefinitions[FRAME_ID_SEND].cycletime = TRANSMISSION_INTERVAL_MILLISECONDS
        config.framedefinitions[FRAME_ID_SEND].signaldefinitions[2].defaultvalue = 25.5
        self.canbus_bcm = canbus.CanBus(config, VIRTUAL_CAN_BUS_NAME, timeout=1.0, use_bcm=True)

        self.simulated_can_process = subprocess.Popen(['candump', VIRTUAL_CAN_BUS_NAME], shell=False,
                                                      universal_newlines=True,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.1)

        self.canbus_bcm.start_sending_all_signals()
        time.sleep(MEASUREMENT_TIME)

        self.canbus_bcm.stop()
        time.sleep(MEASUREMENT_TIME)

        self.canbus_bcm.stop()  # Handle cases with already stopped transmission and reception

        self.simulated_can_process.terminate()
        out, err = self.simulated_can_process.communicate()

        projected_number_of_frames = MEASUREMENT_TIME * 1000 / TRANSMISSION_INTERVAL_MILLISECONDS
        number_of_frames = out.count(" {:03.0f}   [8]  00 00 00 19 00 00 00 00".format(FRAME_ID_SEND))
        self.assertGreaterEqual(number_of_frames, projected_number_of_frames - RESULT_ALLOWED_DIFFERENCE)
        self.assertLessEqual(number_of_frames, projected_number_of_frames + RESULT_ALLOWED_DIFFERENCE)

    def testSendWrongSignal(self):
        self.assertRaises(exceptions.CanException, self.canbus_raw.send_signals, {'unknownsignal': 1})
        self.assertRaises(exceptions.CanException, self.canbus_bcm.send_signals, {'unknownsignal': 1})
        self.assertRaises(exceptions.CanException, self.canbus_raw.send_signals, unknownsignal=1)
        self.assertRaises(exceptions.CanException, self.canbus_bcm.send_signals, unknownsignal=1)
        self.assertRaises(exceptions.CanException, self.canbus_raw.send_signals, "unknownsignal")
        self.assertRaises(exceptions.CanException, self.canbus_bcm.send_signals, "unknownsignal")
        self.assertRaises(exceptions.CanException, self.canbus_raw.send_signals, "unknownsignal", 1)
        self.assertRaises(exceptions.CanException, self.canbus_bcm.send_signals, "unknownsignal", 1)
        self.assertRaises(exceptions.CanException, self.canbus_raw.send_signals)
        self.assertRaises(exceptions.CanException, self.canbus_bcm.send_signals)

    def testSendWrongSignalValue(self):
        self.assertRaises(exceptions.CanException, self.canbus_raw.send_signals, {'testsignal1': 10 ** 10})
        self.assertRaises(exceptions.CanException, self.canbus_bcm.send_signals, {'testsignal1': 10 ** 10})

    def testUsingBcmCommandsForRawInterface(self):
        self.canbus_raw.start_sending_all_signals()
        self.canbus_raw.stop()
        self.canbus_raw.stop_sending()
        self.canbus_raw.stop_reception()

    # Receive signals #

    def testInitReception(self):
        self.canbus_raw.init_reception()
        self.canbus_bcm.init_reception()

    def testReceiveRaw(self):
        canstring = "{:03x}#0102030405060708".format(FRAME_ID_RECEIVE)
        self.simulated_can_process = subprocess.Popen(["cansend", VIRTUAL_CAN_BUS_NAME, canstring],
                                                      shell=False, stderr=subprocess.STDOUT)
        result = self.canbus_raw.recv_next_signals()
        self.assertEqual(len(result), 4)
        self.assertEqual(result['testsignal11'], 0)  # 0
        self.assertEqual(result['testsignal12'], 258)  # 1 * 256 + 2
        self.assertEqual(result['testsignal13'], 1284)  # 5 * 256 + 4

        time.sleep(0.1)
        self.simulated_can_process = subprocess.Popen(["cansend", VIRTUAL_CAN_BUS_NAME, canstring],
                                                      shell=False, stderr=subprocess.STDOUT)
        result = self.canbus_raw.recv_next_signals()
        self.assertEqual(len(result), 4)

    def testReceiveBcmAndStop(self):
        self.canbus_bcm.init_reception()

        canstring = "{:03x}#0102030405060708".format(FRAME_ID_RECEIVE)
        self.simulated_can_process = subprocess.Popen(["cansend", VIRTUAL_CAN_BUS_NAME, canstring],
                                                      shell=False, stderr=subprocess.STDOUT)
        result = self.canbus_bcm.recv_next_signals()
        self.assertEqual(len(result), 4)
        self.assertEqual(result['testsignal11'], 0)  # 0
        self.assertEqual(result['testsignal12'], 258)  # 1 * 256 + 2
        self.assertEqual(result['testsignal13'], 1284)  # 5 * 256 + 4

        time.sleep(0.1)
        self.canbus_bcm.stop_reception()
        self.simulated_can_process = subprocess.Popen(["cansend", VIRTUAL_CAN_BUS_NAME, canstring],
                                                      shell=False, stderr=subprocess.STDOUT)
        self.assertRaises(exceptions.CanTimeoutException, self.canbus_bcm.recv_next_signals)

    def testReceiveBcmFrameAndStop(self):
        self.canbus_bcm.init_reception()

        canstring = "{:03x}#0102030405060708".format(FRAME_ID_RECEIVE)
        self.simulated_can_process = subprocess.Popen(["cansend", VIRTUAL_CAN_BUS_NAME, canstring],
                                                      shell=False, stderr=subprocess.STDOUT)
        result = self.canbus_bcm.recv_next_frame()
        self.assertEqual(len(result), 8)
        self.assertEqual(result.frame_data, b"\x01\x02\x03\x04\x05\x06\x07\x08")

        time.sleep(0.1)
        self.canbus_bcm.stop_reception()
        self.simulated_can_process = subprocess.Popen(["cansend", VIRTUAL_CAN_BUS_NAME, canstring],
                                                      shell=False, stderr=subprocess.STDOUT)
        self.assertRaises(exceptions.CanTimeoutException, self.canbus_bcm.recv_next_frame)

    def testReceiveSpeedRaw(self):
        self.canbus_raw.init_reception()
        self.simulated_can_process = subprocess.Popen(["cangen", VIRTUAL_CAN_BUS_NAME,
                                                       "-I", "{:3x}".format(FRAME_ID_RECEIVE),
                                                       "-L", str(self.FRAME_NUMBER_OF_DATABYTES),
                                                       "-D", "i",
                                                       "-g", str(self.FRAME_SENDER_SPACING_MILLISECONDS)],
                                                      shell=False, stderr=subprocess.STDOUT)
        starttime = time.time()
        for i in range(self.NUMBER_OF_LOOPS):
            self.canbus_raw.recv_next_signals()
        execution_time = time.time() - starttime

        time_per_loop_ms = 1000 * execution_time / self.NUMBER_OF_LOOPS
        frames_per_seconds = self.NUMBER_OF_LOOPS / execution_time
        template = "\n --> Parsed {} RAW frames in {:.1f} s ({:.2f} ms per frame, {:.1f} frames/s). " + \
                   "Frame sender spacing {:.2f} ms.\n"
        output_string = template.format(self.NUMBER_OF_LOOPS, execution_time, time_per_loop_ms, frames_per_seconds,
                                        self.FRAME_SENDER_SPACING_MILLISECONDS)
        print(output_string)

    def testReceiveSpeedBcm(self):
        self.canbus_bcm.init_reception()
        self.simulated_can_process = subprocess.Popen(["cangen", VIRTUAL_CAN_BUS_NAME,
                                                       "-I", "{:3x}".format(FRAME_ID_RECEIVE),
                                                       "-L", str(self.FRAME_NUMBER_OF_DATABYTES),
                                                       "-D", "i",
                                                       "-g", str(self.FRAME_SENDER_SPACING_MILLISECONDS)],
                                                      shell=False, stderr=subprocess.STDOUT)
        starttime = time.time()
        for i in range(self.NUMBER_OF_LOOPS):
            self.canbus_bcm.recv_next_signals()
        execution_time = time.time() - starttime

        time_per_loop_ms = 1000 * execution_time / self.NUMBER_OF_LOOPS
        frames_per_seconds = self.NUMBER_OF_LOOPS / execution_time
        template = "\n --> Parsed {} BCM frames in {:.1f} s ({:.2f} ms per frame, {:.1f} frames/s). " + \
                   "Frame sender spacing {:.2f} ms.\n"
        output_string = template.format(self.NUMBER_OF_LOOPS, execution_time, time_per_loop_ms, frames_per_seconds,
                                        self.FRAME_SENDER_SPACING_MILLISECONDS)
        print(output_string)

    def testReceiveAllSentFramesRaw(self):
        self.canbus_raw.init_reception()
        self.simulated_can_process = subprocess.Popen(["cangen", VIRTUAL_CAN_BUS_NAME,
                                                       "-I", "{:3x}".format(FRAME_ID_RECEIVE),
                                                       "-L", str(self.FRAME_NUMBER_OF_DATABYTES),
                                                       "-D", "i",
                                                       "-g", str(self.FRAME_SENDER_SPACING_MILLISECONDS),
                                                       "-n", str(self.NUMBER_OF_LOOPS)],
                                                      shell=False, stderr=subprocess.STDOUT)
        try:
            for i in range(self.NUMBER_OF_LOOPS):
                self.canbus_raw.recv_next_signals()
        except exceptions.CanTimeoutException:
            raise exceptions.CanTimeoutException("Missed receiving at least one of the {} frames".format(
                self.NUMBER_OF_LOOPS))

    def testReceiveAllSentFramesBcm(self):
        self.canbus_bcm.init_reception()
        self.simulated_can_process = subprocess.Popen(["cangen", VIRTUAL_CAN_BUS_NAME,
                                                       "-I", "{:3x}".format(FRAME_ID_RECEIVE),
                                                       "-L", str(self.FRAME_NUMBER_OF_DATABYTES),
                                                       "-D", "i",
                                                       "-g", str(self.FRAME_SENDER_SPACING_MILLISECONDS),
                                                       "-n", str(self.NUMBER_OF_LOOPS)],
                                                      shell=False, stderr=subprocess.STDOUT)
        try:
            for i in range(self.NUMBER_OF_LOOPS):
                self.canbus_bcm.recv_next_signals()
        except exceptions.CanTimeoutException:
            raise exceptions.CanTimeoutException("Missed receiving at least one of the {} frames".format(
                self.NUMBER_OF_LOOPS))

    def testReceiveNoData(self):
        self.assertRaises(exceptions.CanTimeoutException, self.canbus_raw.recv_next_signals)
        self.assertRaises(exceptions.CanTimeoutException, self.canbus_bcm.recv_next_signals)

    # Save configuration to file #

    def testSaveDefinitionToFileRaw(self):
        try:
            os.remove(self.OUTPUT_FILENAME_4)
        except FileNotFoundError:
            pass

        self.canbus_raw.write_configuration(self.OUTPUT_FILENAME_4)
        self.assertTrue(os.path.exists(self.OUTPUT_FILENAME_4))

    def testSaveLoadedDefinitionToFileRaw(self):
        try:
            os.remove(self.OUTPUT_FILENAME_5)
        except FileNotFoundError:
            pass

        bus = canbus.CanBus.from_kcd_file(self.input_filename, VIRTUAL_CAN_BUS_NAME)
        bus.write_configuration(self.OUTPUT_FILENAME_5)
        self.assertTrue(os.path.exists(self.OUTPUT_FILENAME_5))

    def testSaveDefinitionToFileBcm(self):
        try:
            os.remove(self.OUTPUT_FILENAME_6)
        except FileNotFoundError:
            pass

        self.canbus_bcm.write_configuration(self.OUTPUT_FILENAME_6)
        self.assertTrue(os.path.exists(self.OUTPUT_FILENAME_6))

    def testSaveLoadedDefinitionToFileBcm(self):
        try:
            os.remove(self.OUTPUT_FILENAME_7)
        except FileNotFoundError:
            pass

        bus = canbus.CanBus.from_kcd_file(self.input_filename, VIRTUAL_CAN_BUS_NAME, use_bcm=True)
        bus.write_configuration(self.OUTPUT_FILENAME_7)
        self.assertTrue(os.path.exists(self.OUTPUT_FILENAME_7))


if __name__ == '__main__':

            # Run all tests #
    unittest.main(verbosity=2)

            # Run a single test #
    # suite = unittest.TestSuite()
    # suite.addTest(TestCanBus("testReceiveAllSentFramesRaw"))
    # unittest.TextTestRunner(verbosity=2).run(suite)
