#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_canframedefinition
----------------------------------

Tests for `canframe_definition` module.
"""

import sys
import unittest

assert sys.version_info >= (3, 3, 0), "Python version 3.3 or later required!"

from can4python import exceptions
from can4python import cansignal
from can4python import canframe_definition


class TestCanFrameDefinition(unittest.TestCase):

    def setUp(self):

        self.frame_def = canframe_definition.CanFrameDefinition(1, 'testframedef')
        self.frame_def.producer_ids = set(["9"])
        sig1 = cansignal.CanSignalDefinition('testsignal', 56, 1)  # Least significant bit in last byte
        self.frame_def.signaldefinitions.append(sig1)

    def testConstructor(self):
        fr_def = canframe_definition.CanFrameDefinition(1, 'testframedef', 3)
        self.assertEqual(fr_def.frame_id, 1)
        self.assertEqual(fr_def.dlc, 3)
        self.assertEqual(fr_def.name, 'testframedef')
        self.assertEqual(fr_def.cycletime, None)
        self.assertEqual(fr_def.frame_format, 'standard')
     
    def testConstructorCycletime(self):     
        fr_def = canframe_definition.CanFrameDefinition(1, 'testframedef', 3, 28)
        self.assertEqual(fr_def.frame_id, 1)
        self.assertEqual(fr_def.dlc, 3)
        self.assertEqual(fr_def.name, 'testframedef')
        self.assertEqual(fr_def.cycletime, 28)
        self.assertEqual(fr_def.frame_format, 'standard')
        
    def testConstructorCycletimeNone(self):     
        fr_def = canframe_definition.CanFrameDefinition(0x1FFFFFFF, 'testframedef', 3, None, frame_format='extended')
        self.assertEqual(fr_def.frame_id, 0x1FFFFFFF)
        self.assertEqual(fr_def.dlc, 3)
        self.assertEqual(fr_def.name, 'testframedef')
        self.assertEqual(fr_def.cycletime, None)
        self.assertEqual(fr_def.frame_format, 'extended')
        
    def testConstructorNamedArguments(self):
        fr_def = canframe_definition.CanFrameDefinition(frame_id=1, name='testframedef', dlc=3, cycletime=28)
        self.assertEqual(fr_def.frame_id, 1)
        self.assertEqual(fr_def.dlc, 3)
        self.assertEqual(fr_def.name, 'testframedef')
        self.assertEqual(fr_def.cycletime, 28)
        self.assertEqual(fr_def.frame_format, 'standard')

    def testConstructorWrongValues(self):
        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, -1, 'testframedef')
        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, "1,0", 'testframedef')
        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, None, 'testframedef')
        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, 0x800, 'testframedef',
                          8, 50, 'standard')
        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, 0x20000000, 'testframedef',
                          8, 50, 'extended')

        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, 1, 'testframedef', -1)
        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, 1, 'testframedef', 9)
        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, 1, 'testframedef', "8,0")
        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, 1, 'testframedef', None)

        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, 1, 'testframedef', 8, -3)
        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, 1, 'testframedef', 8, "8,0")

        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, 1, 'testframedef', 8, 50, 'ABC')
        self.assertRaises(exceptions.CanException, canframe_definition.CanFrameDefinition, 1, 'testframedef', 8, 50, 1)

    def testProperties(self):
        self.assertEqual(self.frame_def.frame_id, 1)
        self.assertEqual(self.frame_def.name, 'testframedef')
        self.assertEqual(self.frame_def.dlc, 8)
        self.assertEqual(self.frame_def.cycletime, None)
        self.assertEqual(self.frame_def.throttle_time, None)
        self.assertEqual(self.frame_def.frame_format, 'standard')
        self.assertEqual(self.frame_def.receive_on_change_only, False)
        self.assertEqual(self.frame_def.producer_ids, set(["9"]))

        self.frame_def.frame_id = 2
        self.frame_def.name = 'testframedef2'
        self.frame_def.dlc = 4
        self.frame_def.cycletime = 29
        self.frame_def.throttle_time = 155
        self.frame_def.frame_format = 'extended'
        self.frame_def.receive_on_change_only = True
        self.frame_def.producer_ids = ["9", "1", "1"]

        self.assertEqual(self.frame_def.frame_id, 2)
        self.assertEqual(self.frame_def.name, 'testframedef2')
        self.assertEqual(self.frame_def.dlc, 4)
        self.assertEqual(self.frame_def.cycletime, 29)
        self.assertEqual(self.frame_def.throttle_time, 155)
        self.assertEqual(self.frame_def.frame_format, 'extended')
        self.assertEqual(self.frame_def.receive_on_change_only, True)
        self.assertEqual(self.frame_def.producer_ids, set(["1", "9"]))

        self.frame_def.producer_ids = None
        self.assertEqual(self.frame_def.producer_ids, set())

    def testPropertiesWrongValues(self):
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'frame_id', -1)
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'frame_id', 0x800)
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'frame_id', "1,0")
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'frame_id', None)

        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'dlc', -1)
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'dlc', 9)
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'dlc', "1,0")
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'frame_id', None)

        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'cycletime', -1)
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'cycletime', "1,0")
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'cycletime', 60001)

        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'throttle_time', -1)
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'throttle_time', "1,0")
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'throttle_time', 60001)

        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'frame_format', 'ABC')
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'frame_format', None)
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'frame_format', 1)

        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'producer_ids', 3)
        self.assertRaises(exceptions.CanException, setattr, self.frame_def, 'producer_ids', "3")

    def testIsOutbound(self):
        self.assertTrue(self.frame_def.is_outbound(["9"]))
        self.assertFalse(self.frame_def.is_outbound(["99"]))
        self.assertFalse(self.frame_def.is_outbound([9]))

    def testIsOutboundWrongType(self):
        self.assertRaises(exceptions.CanException, self.frame_def.is_outbound, 9)

    def testGetSignalMask(self):
        testsig2 = cansignal.CanSignalDefinition('testsignal2', 8, 16, endianness='big')  # Two leftmost bytes
        testsig3 = cansignal.CanSignalDefinition('testsignal3', 24, 16, endianness='little',
                                                 maxvalue=1200)  # Two center bytes
        testsig4 = cansignal.CanSignalDefinition('testsignal4', 48, 8, signaltype='signed')  # Second last byte

        self.frame_def.signaldefinitions.append(testsig2)
        self.frame_def.signaldefinitions.append(testsig3)
        self.frame_def.signaldefinitions.append(testsig4)

        self.assertEqual(self.frame_def.get_signal_mask(), b'\xff\xff\x00\xff\xff\x00\xff\x01')

    def testRepr(self):
        print("\n\n\nRepresentation:")
        print(repr(self.frame_def))
        print("Representation (short version):")
        result = self.frame_def.__repr__(long_text=False)
        print(result)  # Check the output manually

        known_result = "CAN frame definition. ID=1 (0x001, standard) 'testframedef', DLC=8, " + \
                       "cycletime None ms, producers: ['9'], no throttling, contains 1 signals"
        self.assertEqual(result.strip(), known_result.strip())

    def testReprThrottling(self):
        fr_def = canframe_definition.CanFrameDefinition(123)
        fr_def.throttle_time = 30  # ms
        result = repr(fr_def)
        
        known_result = "CAN frame definition. ID=123 (0x07B, standard) '', DLC=8, " + \
                       "cycletime None ms, producers: [], throttling 30 ms, contains 0 signals"
        self.assertEqual(result.strip(), known_result.strip())

    def testReprNoSignals(self):
        fr_def = canframe_definition.CanFrameDefinition(1, 'testframedef')
        result = repr(fr_def)
        
        known_result = "CAN frame definition. ID=1 (0x001, standard) 'testframedef', DLC=8, " + \
                       "cycletime None ms, producers: [], no throttling, contains 0 signals"
        self.assertEqual(result.strip(), known_result.strip())

    def testGetDescriptiveAsciiArt(self):       
        result = self.frame_def.get_descriptive_ascii_art()
        print('\n\n' + result)  # Check the output manually
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
