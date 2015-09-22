#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_canframe
----------------------------------

Tests for `canframe` module.
"""

import sys
import unittest

assert sys.version_info >= (3, 3, 0), "Python version 3.3 or later required!"

from can4python import exceptions
from can4python import cansignal
from can4python import canframe_definition
from can4python import canframe


class TestCanFrame(unittest.TestCase):

    def setUp(self):
        self.frame = canframe.CanFrame(1, b'\x00\x02\x00\x08\x00\x00\x00\xff')

        self.testsig1 = cansignal.CanSignalDefinition('testsignal1', 56, 1)  # Least significant bit in last byte
        self.testsig2 = cansignal.CanSignalDefinition('testsignal2', 8, 16, endianness='big')  # Two leftmost bytes
        self.testsig3 = cansignal.CanSignalDefinition('testsignal3', 24, 16, endianness='little',
                                                      maxvalue=1200)  # Two center bytes
        self.testsig4 = cansignal.CanSignalDefinition('testsignal4', 48, 8, signaltype='signed')  # Second last byte

        self.frame_def = canframe_definition.CanFrameDefinition(1, 'testmessage')
        self.frame_def.signaldefinitions.append(self.testsig1)
        self.frame_def.signaldefinitions.append(self.testsig2)
        self.frame_def.signaldefinitions.append(self.testsig3)
        self.frame_def.signaldefinitions.append(self.testsig4)

    def testConstructor(self):
        frame1 = canframe.CanFrame(0x7FF, b'\x02', 'standard')
        self.assertEqual(frame1.frame_id, 0x7FF)
        self.assertEqual(frame1.frame_data, b'\x02')
        self.assertEqual(frame1.frame_format, 'standard')

        frame2 = canframe.CanFrame(0x1FFFFFFF, b'\x02\x03', 'extended')
        self.assertEqual(frame2.frame_id, 0x1FFFFFFF)
        self.assertEqual(frame2.frame_data, b'\x02\x03')
        self.assertEqual(frame2.frame_format, 'extended')
        
    def testConstructorNamedArguments(self):   
        frame = canframe.CanFrame(frame_id=3, frame_data=b'\x04', frame_format='extended')
        self.assertEqual(frame.frame_id, 3)
        self.assertEqual(frame.frame_data, b'\x04')
        self.assertEqual(frame.frame_format, 'extended')
  
    def testConstructorFromEmptyBytes(self):       
        frame = canframe.CanFrame.from_empty_bytes(5, 6, 'extended')
        self.assertEqual(frame.frame_id, 5)
        self.assertEqual(frame.frame_data, b'\x00\x00\x00\x00\x00\x00')
        self.assertEqual(frame.frame_format, 'extended')
        
    def testConstructorFromRawframes(self):       
        frame1 = canframe.CanFrame.from_rawframe(b'\x07\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(frame1.frame_id, 7)
        self.assertEqual(frame1.frame_format, 'standard')
        self.assertEqual(frame1.frame_data, b'\x00\x00\x00\x00\x00\x00\x00\x00')

        frame2 = canframe.CanFrame.from_rawframe(b'\x03\x00\x00\x80\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(frame2.frame_id, 3)
        self.assertEqual(frame2.frame_format, 'extended')
        self.assertEqual(frame2.frame_data, b'\x00\x00\x00\x00\x00\x00')

    def testWrongConstructor(self):
        self.assertRaises(exceptions.CanException, canframe.CanFrame, -1, b'\x01')
        self.assertRaises(exceptions.CanException, canframe.CanFrame, None, b'\x01')
        self.assertRaises(exceptions.CanException, canframe.CanFrame, 0x800, b'\x01')
        self.assertRaises(exceptions.CanException, canframe.CanFrame, 0x800, b'\x01', 'standard')
        self.assertRaises(exceptions.CanException, canframe.CanFrame, 0x20000000, b'\x01', 'extended')
        self.assertRaises(exceptions.CanException, canframe.CanFrame, "1,0", b'\x01')
        self.assertRaises(exceptions.CanException, canframe.CanFrame, 1, "ABC")
        self.assertRaises(exceptions.CanException, canframe.CanFrame, 1, "123")
        self.assertRaises(exceptions.CanException, canframe.CanFrame, 1, None)
        self.assertRaises(exceptions.CanException, canframe.CanFrame, 1, b'\x01\x02\x03\x04\x05\x06\x07\x08\x09')
        self.assertRaises(exceptions.CanException, canframe.CanFrame, 1, b'\x01', "ABC")
        self.assertRaises(exceptions.CanException, canframe.CanFrame, 1, b'\x01', 0)
        self.assertRaises(exceptions.CanException, canframe.CanFrame, 1, b'\x01', None)

    def testWrongConstructorFromEmptyBytes(self):
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, "ABC", 8)
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, "ABC", 8, 'standard')
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, "ABC", 8, 'extended')
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, -1, 8)
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, None, 8)
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, 1, 9)
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, 1, -1)
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, 1, None)
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, 1, "ABC")
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, 1, 8, "ABC")
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_empty_bytes, 1, 8, None)

    def testWrongConstructorFromRawframe(self):
        self.assertRaises(exceptions.CanException, canframe.CanFrame.from_rawframe,
                          b'\x01\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF')

    def testFrameidGet(self):
        self.assertEqual(self.frame.frame_id, 1)

    def testFrameidSet(self):
        known_values = [0, 1, 100, 1000]
        for value in known_values:
            self.frame.frame_id = value
            self.assertEqual(self.frame.frame_id, value)

    def testFrameidSetWrongValue(self):
        self.assertRaises(exceptions.CanException, setattr, self.frame, 'frame_id', -1)
        self.assertRaises(exceptions.CanException, setattr, self.frame, 'frame_id', 0x800)
        self.assertRaises(exceptions.CanException, setattr, self.frame, 'frame_id', "1,0")
        self.assertRaises(exceptions.CanException, setattr, self.frame, 'frame_id', None)

    def testFrameFormatGet(self):
        self.assertEqual(self.frame.frame_format, 'standard')

    def testFrameFormatSet(self):
        known_values = ['standard', 'extended']
        for value in known_values:
            self.frame.frame_format = value
            self.assertEqual(self.frame.frame_format, value)

    def testFrameFormatSetWrongValue(self):
        self.assertRaises(exceptions.CanException, setattr, self.frame, 'frame_format', 7)
        self.assertRaises(exceptions.CanException, setattr, self.frame, 'frame_format', 'ABC')

    def testFramedataGet(self):
        self.assertEqual(self.frame.frame_data, b'\x00\x02\x00\x08\x00\x00\x00\xff')

    def testFramedataSet(self):
        known_values = [b'', b'\x00', b'\x01\x02\x03\x04\x05\x06\x07\x08']
        for value in known_values:
            self.frame.frame_data = value
            self.assertEqual(self.frame.frame_data, value)

    def testFramedataSetWrongValue(self):
        self.assertRaises(exceptions.CanException, setattr, self.frame, 'frame_data',
                          b'\x01\x02\x03\x04\x05\x06\x07\x08\x09')
        self.assertRaises(exceptions.CanException, setattr, self.frame, 'frame_data', None)
        self.assertRaises(exceptions.CanException, setattr, self.frame, 'frame_data', "7")
        self.assertRaises(exceptions.CanException, setattr, self.frame, 'frame_data', "\x01")

    def testSignalvalueSet(self):       
        self.frame.set_signalvalue(self.testsig1)
        self.frame.set_signalvalue(self.testsig1, 0)
        self.frame.set_signalvalue(self.testsig1, 1)
        self.frame.set_signalvalue(self.testsig1, 0)
        self.frame.set_signalvalue(self.testsig2, 1000)
        self.frame.set_signalvalue(self.testsig2, 27.3)
        self.frame.set_signalvalue(self.testsig2, 0)
        self.frame.set_signalvalue(self.testsig3, 1000)
        self.frame.set_signalvalue(self.testsig3, 0)
        self.assertEqual(self.frame.frame_data, b'\x00\x00\x00\x00\x00\x00\x00\xfe')
        
        self.frame.set_signalvalue(self.testsig1, 1)
        self.frame.set_signalvalue(self.testsig2, 16)
        self.frame.set_signalvalue(self.testsig3, 512)
        self.assertEqual(self.frame.frame_data, b'\x00\x10\x00\x00\x02\x00\x00\xff')

        self.frame.set_signalvalue(self.testsig3, 1500)  # Limited to 1200
        self.assertEqual(self.frame.get_signalvalue(self.testsig3), 1200)

    def testSignalvalueSetSigned(self):
        self.frame.frame_data = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        self.frame.set_signalvalue(self.testsig4, -1)
        self.assertEqual(self.frame.frame_data, b'\x00\x00\x00\x00\x00\x00\xff\x00')
        self.frame.set_signalvalue(self.testsig4, -128)
        self.assertEqual(self.frame.frame_data, b'\x00\x00\x00\x00\x00\x00\x80\x00')

    def testSignalvalueSetSingle(self):
        testsig1 = cansignal.CanSignalDefinition('testsignal1', 56, 32, endianness='big', signaltype='single')
        frame1 = canframe.CanFrame(1, b'\x00\x00\x00\x00\x00\x00\x00\x00')

        # Example from https://en.wikipedia.org/wiki/Single-precision_floating-point_format
        frame1.set_signalvalue(testsig1, 0.15625)
        self.assertEqual(frame1.frame_data, b'\x00\x00\x00\x00\x3E\x20\x00\x00')

    def testSignalvalueSetSingleLittle(self):
        testsig1 = cansignal.CanSignalDefinition('testsignal1', 32, 32, endianness='little', signaltype='single')
        print(testsig1.get_descriptive_ascii_art())
        frame1 = canframe.CanFrame(1, b'\x00\x00\x00\x00\x00\x00\x00\x00')

        # Example from https://en.wikipedia.org/wiki/Single-precision_floating-point_format
        frame1.set_signalvalue(testsig1, 0.15625)
        self.assertEqual(frame1.frame_data, b'\x00\x00\x00\x00\x00\x00\x20\x3E')

    def testSignalvalueGetSingle(self):
        testsig1 = cansignal.CanSignalDefinition('testsignal1', 56, 32, endianness='big', signaltype='single')

        # Example from https://en.wikipedia.org/wiki/Single-precision_floating-point_format
        frame1 = canframe.CanFrame(1, b'\x00\x00\x00\x00\x3E\x20\x00\x00')
        self.assertAlmostEqual(frame1.get_signalvalue(testsig1), 0.15625)

    def testSignalvalueGetSingleLittle(self):
        testsig1 = cansignal.CanSignalDefinition('testsignal1', 32, 32, endianness='little', signaltype='single')

        # Example from https://en.wikipedia.org/wiki/Single-precision_floating-point_format
        frame1 = canframe.CanFrame(1, b'\x00\x00\x00\x00\x00\x00\x20\x3E')
        self.assertAlmostEqual(frame1.get_signalvalue(testsig1), 0.15625)

    def testSignalvalueSetDouble(self):
        testsig1 = cansignal.CanSignalDefinition('testsignal1', 56, 64, endianness='big', signaltype='double')
        frame1 = canframe.CanFrame(1, b'\x00\x00\x00\x00\x00\x00\x00\x00')

        # Example from https://en.wikipedia.org/wiki/Double-precision_floating-point_format
        frame1.set_signalvalue(testsig1, 2.0)
        self.assertEqual(frame1.frame_data, b'\x40\x00\x00\x00\x00\x00\x00\x00')

        frame1.set_signalvalue(testsig1, 1.0)
        self.assertEqual(frame1.frame_data, b'\x3F\xF0\x00\x00\x00\x00\x00\x00')

    def testSignalvalueSetDoubleLittle(self):
        testsig1 = cansignal.CanSignalDefinition('testsignal1', 0, 64, endianness='little', signaltype='double')
        frame1 = canframe.CanFrame(1, b'\x00\x00\x00\x00\x00\x00\x00\x00')

        # Example from https://en.wikipedia.org/wiki/Double-precision_floating-point_format
        frame1.set_signalvalue(testsig1, 2.0)
        self.assertEqual(frame1.frame_data, b'\x00\x00\x00\x00\x00\x00\x00\x40')

    def testSignalvalueGetDouble(self):
        testsig1 = cansignal.CanSignalDefinition('testsignal1', 56, 64, endianness='big', signaltype='double')

        # Example from https://en.wikipedia.org/wiki/Single-precision_floating-point_format
        frame1 = canframe.CanFrame(1, b'\x40\x00\x00\x00\x00\x00\x00\x00')
        self.assertAlmostEqual(frame1.get_signalvalue(testsig1), 2.0)

        frame1 = canframe.CanFrame(1, b'\x3F\xF0\x00\x00\x00\x00\x00\x00')
        self.assertAlmostEqual(frame1.get_signalvalue(testsig1), 1.0)

        frame1 = canframe.CanFrame(1, b'\x3F\xF0\x00\x00\x00\x00\x00\x01')
        self.assertAlmostEqual(frame1.get_signalvalue(testsig1), 1.0)

        frame1 = canframe.CanFrame(1, b'\x7F\xEF\xFF\xFF\xFF\xFF\xFF\xFF')
        self.assertAlmostEqual(frame1.get_signalvalue(testsig1), 1.7976931348623157e308)

    def testSignalvalueGetDoubleLittle(self):
        testsig1 = cansignal.CanSignalDefinition('testsignal1', 0, 64, endianness='little', signaltype='double')

        # Example from https://en.wikipedia.org/wiki/Single-precision_floating-point_format
        frame1 = canframe.CanFrame(1, b'\x00\x00\x00\x00\x00\x00\xF0\x3F')
        self.assertAlmostEqual(frame1.get_signalvalue(testsig1), 1.0)

    def testSignalvalueSetTooShortFrame(self):
        self.frame.frame_data = b'\00'
        self.assertRaises(exceptions.CanException, self.frame.set_signalvalue, self.testsig1)


    def testSignalvalueGetSetMin(self):
        self.testsig3.minvalue = 0
        self.frame.set_signalvalue(self.testsig3, 0)
        self.assertEqual(self.frame.get_signalvalue(self.testsig3), 0)

        self.testsig3.minvalue = 100
        self.assertEqual(self.frame.get_signalvalue(self.testsig3), 100)  # Minvalue for get

        self.testsig3.minvalue = 400
        self.frame.set_signalvalue(self.testsig3, 60)  # Minvalue for set
        self.testsig3.minvalue = 10
        self.assertEqual(self.frame.get_signalvalue(self.testsig3), 400)

    def testSignalvalueGetSetMax(self):
        self.testsig3.maxvalue = 800
        self.frame.set_signalvalue(self.testsig3, 900)  # Maxvalue for set
        self.assertEqual(self.frame.get_signalvalue(self.testsig3), 800)

        self.testsig3.maxvalue = 100
        self.assertEqual(self.frame.get_signalvalue(self.testsig3), 100)  # Maxvalue for get

    def testSignalvalueSetWrongValue(self):
        self.assertRaises(exceptions.CanException, self.frame.set_signalvalue, self.testsig1, -1)
        self.assertRaises(exceptions.CanException, self.frame.set_signalvalue, self.testsig1, 2)

    def testSignalvalueGet(self):
        self.assertEqual(self.frame.get_signalvalue(self.testsig1), 1)
        self.assertEqual(self.frame.get_signalvalue(self.testsig2), 2)
        self.assertEqual(self.frame.get_signalvalue(self.testsig3), 8)

    def testSignalvalueGetSigned(self):
        self.frame.frame_data = b'\x00\x00\x00\x00\x00\x00\x80\x00'
        self.assertEqual(self.frame.get_signalvalue(self.testsig4), -128)

    def testGetRawFrameStandard(self):
        self.assertEqual(self.frame.get_rawframe(),
                         b'\x01\x00\x00\x00\x08\x00\x00\x00\x00\x02\x00\x08\x00\x00\x00\xff')

    def testGetRawFrameExtended(self):
        self.frame.frame_format = 'extended'
        self.assertEqual(self.frame.get_rawframe(),
                         b'\x01\x00\x00\x80\x08\x00\x00\x00\x00\x02\x00\x08\x00\x00\x00\xff')

    def testUnpack(self):
        frame_defs = {self.frame_def.frame_id: self.frame_def}
        result = self.frame.unpack(frame_defs)
        self.assertEqual(len(result), 4)
        self.assertEqual(result['testsignal1'], 1)
        self.assertEqual(result['testsignal2'], 2)
        self.assertEqual(result['testsignal3'], 8)
        self.assertEqual(result['testsignal4'], 0)

    def testUnpackWrongFrameId(self):
        self.frame.frame_id = 2
        frame_defs = {self.frame_def.frame_id: self.frame_def}
        result = self.frame.unpack(frame_defs)
        self.assertEqual(len(result), 0)

    def testUnpackWrongFramelength(self):
        self.frame.frame_data = b'\x00\x02'
        frame_defs = {self.frame_def.frame_id: self.frame_def}
        self.assertRaises(exceptions.CanException, self.frame.unpack, frame_defs)

    def testRepr(self):
        result = repr(self.frame)
        known_result = "CAN frame ID: 1 (0x001, standard) data: 00 02 00 08 00 00 00 FF (8 bytes)"
        self.assertEqual(result.strip(), known_result.strip())

    def testLen(self):
        self.assertEqual(len(self.frame), 8)
        self.assertEqual(len(self.frame.frame_data), 8)

    def testGetDescriptiveAsciiArt(self):
        result = self.frame.get_descriptive_ascii_art()
        print('\n\n' + result)  # Check the output manually
        

if __name__ == '__main__':
        
        # Run all tests #
    unittest.main()
    
        # Run a single test #
    # suite = unittest.TestSuite()
    # suite.addTest(TestCanFrame("testGetDescriptiveAsciiArt"))
    # unittest.TextTestRunner(verbosity=2).run(suite)

