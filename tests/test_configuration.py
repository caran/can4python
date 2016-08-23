#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_configuration
----------------------------------

Tests for `configuration` module.
"""

import copy
import os
import sys
import unittest

assert sys.version_info >= (3, 3, 0), "Python version 3.3 or later required!"

from can4python import canframe_definition
from can4python import cansignal
from can4python import configuration
from can4python import exceptions

FRAME_ID_SEND = 7
FRAME_ID_RECEIVE = 12
NON_EXISTING_FRAME_ID = 99

testsig1 = cansignal.CanSignalDefinition('testsignal1', 56, 1)  # Least significant bit in last byte
testsig2 = cansignal.CanSignalDefinition('testsignal2', 8, 16, endianness='big')  # Two leftmost bytes
testsig3 = cansignal.CanSignalDefinition('testsignal3', 24, 16, endianness='little')  # Two center bytes
testsig4 = cansignal.CanSignalDefinition('testsignal4', 59, 4, endianness='big', signaltype='signed')
fr_def1 = canframe_definition.CanFrameDefinition(FRAME_ID_SEND, 'testframedef_send')
fr_def1.producer_ids = ["1"]
fr_def1.signaldefinitions.append(testsig1)
fr_def1.signaldefinitions.append(testsig2)
fr_def1.signaldefinitions.append(testsig3)
fr_def1.signaldefinitions.append(testsig4)
testsig11 = cansignal.CanSignalDefinition('testsignal11', 56, 1)  # Least significant bit in last byte
testsig12 = cansignal.CanSignalDefinition('testsignal12', 8, 16, endianness='big')  # Two leftmost bytes
testsig13 = cansignal.CanSignalDefinition('testsignal13', 24, 16, endianness='little')  # Two center bytes
testsig14 = cansignal.CanSignalDefinition('testsignal14', 59, 4, endianness='big', signaltype='signed')
fr_def2 = canframe_definition.CanFrameDefinition(FRAME_ID_RECEIVE, 'testframedef_receive')
fr_def2.producer_ids = ["77"]
fr_def2.signaldefinitions.append(testsig11)
fr_def2.signaldefinitions.append(testsig12)
fr_def2.signaldefinitions.append(testsig13)
fr_def2.signaldefinitions.append(testsig14)

TESTCONFIG1 = configuration.Configuration()
TESTCONFIG1.add_framedefinition(fr_def1)
TESTCONFIG1.add_framedefinition(fr_def2)
TESTCONFIG1.busname = "bus1"
TESTCONFIG1.ego_node_ids = ["1", "33", "45A", "A",]

class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.config = copy.deepcopy(TESTCONFIG1)

    def testConstructor(self):
        config = configuration.Configuration()
        self.assertEqual(config.framedefinitions, {})
        self.assertEqual(config.busname, None)

        config = configuration.Configuration(None, "ABC")
        self.assertEqual(config.framedefinitions, {})
        self.assertEqual(config.busname, "ABC")

        config = configuration.Configuration(None, "ABC", ["1", "2", "3"])
        self.assertEqual(config.framedefinitions, {})
        self.assertEqual(config.busname, "ABC")
        self.assertEqual(config.ego_node_ids, set(["1", "2", "3"]))

        fr_def = canframe_definition.CanFrameDefinition(1, 'testframedef')
        sig1 = cansignal.CanSignalDefinition('testsignal', 56, 1)  # Least significant bit in last byte
        fr_def.signaldefinitions.append(sig1)
        config = configuration.Configuration({1:fr_def}, "DEF")
        self.assertEqual(config.framedefinitions[1], fr_def)
        self.assertEqual(config.busname, "DEF")

    def testRepr(self):
        result = repr(self.config)
        known_result = \
            "CAN configuration object. Busname 'bus1', having 2 frameIDs defined. Enacts these node IDs: 1 33 45A A"
        self.assertEqual(result.strip(), known_result.strip())

    def testProperties(self):
        self.assertEqual(self.config.framedefinitions[FRAME_ID_SEND].frame_id, FRAME_ID_SEND)
        self.assertEqual(self.config.ego_node_ids, set(["A", "1", "33", "45A"]))
        self.config.ego_node_ids = ["1", "1", "1", "2", "2", 3]
        self.assertEqual(self.config.ego_node_ids, set(["1", "2", "3"]))

    def testPropertiesWrongValues(self):
        self.assertRaises(exceptions.CanException, setattr, self.config, 'ego_node_ids', 3)
        self.assertRaises(exceptions.CanException, setattr, self.config, 'ego_node_ids', "3")

    def testSetThrottleTimes(self):
        self.assertEqual(self.config.framedefinitions[FRAME_ID_SEND].throttle_time, None)
        self.config.set_throttle_times({FRAME_ID_SEND: 123})
        self.assertEqual(self.config.framedefinitions[FRAME_ID_SEND].throttle_time, 123)

    def testSetThrottleTimesWrongValues(self):
        self.assertRaises(exceptions.CanException, self.config.set_throttle_times, {NON_EXISTING_FRAME_ID: 123})
        self.assertRaises(exceptions.CanException, self.config.set_throttle_times, "ABC")
        self.assertRaises(exceptions.CanException, self.config.set_throttle_times, 123)

    def testSetThrottleTimesFromSignalnames(self):
        self.assertEqual(self.config.framedefinitions[FRAME_ID_SEND].throttle_time, None)
        self.config.set_throttle_times_from_signalnames({'testsignal1': 125})
        self.assertEqual(self.config.framedefinitions[FRAME_ID_SEND].throttle_time, 125)
        self.config.set_throttle_times_from_signalnames({'testsignal2': 126})
        self.assertEqual(self.config.framedefinitions[FRAME_ID_SEND].throttle_time, 126)

    def testSetThrottleTimesFromSignalnamesWrongValues(self):
        self.assertRaises(exceptions.CanException,
                          self.config.set_throttle_times_from_signalnames, {"nonexistingsignal": 123})
        self.assertRaises(exceptions.CanException, self.config.set_throttle_times_from_signalnames, "ABC")
        self.assertRaises(exceptions.CanException, self.config.set_throttle_times_from_signalnames, 123)

    def testSetReceiveOnChangeOnly(self):
        self.assertEqual(self.config.framedefinitions[FRAME_ID_SEND].receive_on_change_only, False)
        self.config.set_receive_on_change_only([FRAME_ID_SEND])
        self.assertEqual(self.config.framedefinitions[FRAME_ID_SEND].receive_on_change_only, True)

    def testSetReceiveOnChangeOnlyWrongValue(self):
        self.assertRaises(exceptions.CanException, self.config.set_receive_on_change_only, [NON_EXISTING_FRAME_ID])
        self.assertRaises(exceptions.CanException, self.config.set_receive_on_change_only, "ABC")
        self.assertRaises(exceptions.CanException, self.config.set_receive_on_change_only, 123)

    def testSetReceiveOnChangeOnlyFromSignalnames(self):
        self.assertEqual(self.config.framedefinitions[FRAME_ID_SEND].receive_on_change_only, False)
        self.config.set_receive_on_change_only_from_signalnames(['testsignal1'])
        self.assertEqual(self.config.framedefinitions[FRAME_ID_SEND].receive_on_change_only, True)

    def testSetReceiveOnChangeOnlyFromSignalnamesWrongValues(self):
        self.assertRaises(exceptions.CanException,
                          self.config.set_receive_on_change_only_from_signalnames, ["nonexistingsignal"])
        self.assertRaises(exceptions.CanException, self.config.set_receive_on_change_only_from_signalnames, "ABC")
        self.assertRaises(exceptions.CanException, self.config.set_receive_on_change_only_from_signalnames, 123)
        
    def testGetDescriptiveAsciiArt(self):
        result = self.config.get_descriptive_ascii_art()
        print('\n\n' + result)  # Check the output manually

    def testAddFramedefinition(self):
        config = configuration.Configuration()
        fr_def = canframe_definition.CanFrameDefinition(1, 'testframedef')
        config.add_framedefinition(fr_def)
        self.assertEqual(config.framedefinitions[1], fr_def)
        self.assertEqual(config.busname, None)

if __name__ == '__main__':
    unittest.main()
