#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cansignal
----------------------------------

Tests for `cansignal` module.
"""

import sys
import unittest

assert sys.version_info >= (3, 3, 0), "Python version 3.3 or later required!"

from can4python import constants
from can4python import exceptions
from can4python import cansignal


class TestCanSignal(unittest.TestCase):

    def setUp(self):
        self.signal = cansignal.CanSignalDefinition('testsignal', 56, 1)  # Least significant bit in last byte

    def testConstructor(self):
        sig = cansignal.CanSignalDefinition('testsignal', 56, 1)  # Least significant bit in last byte
        self.assertEqual(sig.signalname, 'testsignal')
        self.assertEqual(sig.startbit, 56)
        self.assertEqual(sig.numberofbits, 1)
        self.assertEqual(sig.scalingfactor, 1)
        self.assertEqual(sig.valueoffset, 0)
        self.assertEqual(sig.endianness, 'little')
        self.assertEqual(sig.signaltype, 'unsigned')
        self.assertEqual(sig.minvalue, None)
        self.assertEqual(sig.maxvalue, None)
        self.assertEqual(sig.defaultvalue, 0)
        
        sig = cansignal.CanSignalDefinition('testsignal2', 7, 1, endianness='big')  # Most significant bit in first byte
        self.assertEqual(sig.signalname, 'testsignal2')
        self.assertEqual(sig.startbit, 7)
        self.assertEqual(sig.numberofbits, 1)
        self.assertEqual(sig.scalingfactor, 1)
        self.assertEqual(sig.valueoffset, 0)
        self.assertEqual(sig.endianness, 'big')
        self.assertEqual(sig.signaltype, 'unsigned')
        self.assertEqual(sig.minvalue, None)
        self.assertEqual(sig.maxvalue, None)
        self.assertEqual(sig.defaultvalue, 0)       
        
        sig = cansignal.CanSignalDefinition('testsignal3', 56, 1, defaultvalue=1)  # Least significant bit in last byte
        self.assertEqual(sig.signalname, 'testsignal3')
        self.assertEqual(sig.startbit, 56)
        self.assertEqual(sig.numberofbits, 1)
        self.assertEqual(sig.scalingfactor, 1)
        self.assertEqual(sig.valueoffset, 0)
        self.assertEqual(sig.endianness, 'little')
        self.assertEqual(sig.signaltype, 'unsigned')
        self.assertEqual(sig.minvalue, None)
        self.assertEqual(sig.maxvalue, None)
        self.assertEqual(sig.defaultvalue, 1)

    def testConstructorWrongValues(self):
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', 63, 1, scalingfactor=-1)
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', 64, 1)
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', -1, 1)
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', 56, 0)
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', 56, 65)
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition,
                          'testsignal', 63, 2, endianness='little')  # Owerflows to bitnumber 64
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition,
                          'testsignal', 7, 2, endianness='big')  # Owerflows to the left

        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', 20, 5, "ABC")
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', 20, 5, None)
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', 20, 5, "1,0")

        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', 20, 5, 1, None)
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', 20, 5, 1, "ABC")
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition, 'testsignal', 20, 5, 1, "1,0")

        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition,
                          'testsignal', 56, 1, endianness='A')
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition,
                          'testsignal', 56, 1, endianness=2)
        self.assertRaises(exceptions.CanException, cansignal.CanSignalDefinition,
                          'testsignal', 56, 1, endianness=None)

    def testProperties(self):
        self.assertEqual(self.signal.signalname, 'testsignal')
        self.assertEqual(self.signal.startbit, 56)
        self.assertEqual(self.signal.numberofbits, 1)
        self.assertEqual(self.signal.scalingfactor, 1)
        self.assertEqual(self.signal.valueoffset, 0)
        self.assertEqual(self.signal.endianness, constants.LITTLE_ENDIAN)
        self.assertEqual(self.signal.signaltype, constants.CAN_SIGNALTYPE_UNSIGNED)
        self.assertEqual(self.signal.maxvalue, None)
        self.assertEqual(self.signal.minvalue, None)

        self.signal.signalname = 'testsignal2'
        self.signal.startbit = 55
        self.signal.numberofbits = 2
        self.signal.scalingfactor = 2
        self.signal.valueoffset = 1
        self.signal.maxvalue = 4.1
        self.signal.minvalue = 3.2
        self.signal.defaultvalue = 3.7
        self.signal.endianness = constants.BIG_ENDIAN
        self.signal.signaltype = constants.CAN_SIGNALTYPE_SIGNED
        self.signal.unit = 'm/s'
        self.signal.comment = "ABC"

        self.assertEqual(self.signal.signalname, 'testsignal2')
        self.assertEqual(self.signal.startbit, 55)
        self.assertEqual(self.signal.numberofbits, 2)
        self.assertEqual(self.signal.scalingfactor, 2)
        self.assertEqual(self.signal.valueoffset, 1)
        self.assertEqual(self.signal.maxvalue, 4.1)
        self.assertEqual(self.signal.minvalue, 3.2)
        self.assertEqual(self.signal.defaultvalue, 3.7)
        self.assertEqual(self.signal.endianness, constants.BIG_ENDIAN)
        self.assertEqual(self.signal.signaltype, constants.CAN_SIGNALTYPE_SIGNED)
        self.assertEqual(self.signal.unit, 'm/s')
        self.assertEqual(self.signal.comment, "ABC")

    def testPropertiesWrongValues(self):
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'startbit', -1)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'startbit', 64)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'startbit', None)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'numberofbits', -1)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'numberofbits', 0)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'numberofbits', None)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'endianness', 1)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'endianness', 'ABC')
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'endianness', None)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'signaltype', 1)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'signaltype', 'ABC')
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'signaltype', None)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'maxvalue', 2)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'maxvalue', -1)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'maxvalue', 'ABC')
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'minvalue', -1)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'minvalue', 2)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'minvalue', 'ABC')
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'defaultvalue', -1)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'defaultvalue', 2)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'defaultvalue', 'ABC')
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'scalingfactor', 'ABC')
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'scalingfactor', None)
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'valueoffset', 'ABC')
        self.assertRaises(exceptions.CanException, setattr, self.signal, 'valueoffset', None)

        sig = cansignal.CanSignalDefinition('testsignal', 56, 1, endianness='big')
        sig.signaltype = constants.CAN_SIGNALTYPE_SINGLE
        self.assertRaises(exceptions.CanException, setattr, sig, 'numberofbits', 31)

        sig.signaltype = constants.CAN_SIGNALTYPE_DOUBLE
        self.assertRaises(exceptions.CanException, setattr, sig, 'numberofbits', 63)

    def testRepr(self):
        print('\nOutput from repr():')  # Check the output manually
        sig = cansignal.CanSignalDefinition('testsignal', 56, 1, comment="ABC")
        print(repr(sig))

        comment = "ABC" + " " * 100
        sig = cansignal.CanSignalDefinition('testsignal', 56, 1, comment=comment, endianness='big')
        print(repr(sig))

    def testGetDescriptiveAsciiArt(self):
        print('\nOutput from get_descriptive_ascii_art():')  # Check the output manually
        sig = cansignal.CanSignalDefinition('testsignalA', 56, 1)
        print(sig.get_descriptive_ascii_art())

        sig = cansignal.CanSignalDefinition('testsignalB', 54, 4)
        print(sig.get_descriptive_ascii_art())

        sig = cansignal.CanSignalDefinition('testsignalC', 54, 2, endianness='big')
        print(sig.get_descriptive_ascii_art())

        sig = cansignal.CanSignalDefinition('testsignalD', 54, 4, endianness='big')
        print(sig.get_descriptive_ascii_art())

    def testMaximumPossibleValueGet(self):
        sig = cansignal.CanSignalDefinition('testsignal', 56, 3, scalingfactor=2, valueoffset=10)
        result = sig.get_maximum_possible_value()
        self.assertEqual(result, 24)

    def testMinimumPossibleValueGet(self):
        sig = cansignal.CanSignalDefinition('testsignal', 56, 3, scalingfactor=2, valueoffset=10)
        result = sig.get_minimum_possible_value()
        self.assertEqual(result, 10)

    def testGetMinimumDlc(self):
        sig = cansignal.CanSignalDefinition('testsignal', 56, 3)
        result = sig.get_minimum_dlc()
        self.assertEqual(result, 8)

        sig = cansignal.CanSignalDefinition('testsignal', 2, 3)
        result = sig.get_minimum_dlc()
        self.assertEqual(result, 1)


if __name__ == '__main__':
    print("\n" * 10)
    unittest.main()
