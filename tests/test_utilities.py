#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_utilities
----------------------------------

Tests for `utilities` module.
"""

import sys
import unittest

assert sys.version_info >= (3, 3, 0), "Python version 3.3 or later required!"

from can4python import utilities
from can4python import exceptions


class TestCalculateBackwardBitnumber(unittest.TestCase):

    knownValues = (
        (0, 56),
        (1, 57),
        (7, 63),
        (56, 0),
        (63, 7)
    )

    def test_known_values(self):
        for normal, backwards in self.knownValues:
            result = utilities.calculate_backward_bitnumber(normal)
            self.assertEqual(result, backwards)

    def testWrongInputValue(self):
        self.assertRaises(exceptions.CanException, utilities.calculate_backward_bitnumber, -1)
        self.assertRaises(exceptions.CanException, utilities.calculate_backward_bitnumber, 64)


class TestCalculateNormalBitnumber(unittest.TestCase):

    knownValues = TestCalculateBackwardBitnumber.knownValues

    def test_known_values(self):
        for normal, backwards in self.knownValues:
            result = utilities.calculate_normal_bitnumber(backwards)
            self.assertEqual(normal, result)

    def testWrongInputValue(self):
        self.assertRaises(exceptions.CanException, utilities.calculate_normal_bitnumber, -1)
        self.assertRaises(exceptions.CanException, utilities.calculate_normal_bitnumber, 64)


class TestSanityBitnumber(unittest.TestCase):

    def test_known_values(self):
        for normal_bitnumber in range(64):
            backward_bitnumber = utilities.calculate_backward_bitnumber(normal_bitnumber)
            result = utilities.calculate_normal_bitnumber(backward_bitnumber)
            self.assertEqual(result, normal_bitnumber)


class TestGenerateBitByteOverview(unittest.TestCase):

    def test_known_values(self):
        inputstring = '1' + ' ' * 63
        utilities.generate_bit_byte_overview(inputstring)
        utilities.generate_bit_byte_overview(inputstring, 0)
        utilities.generate_bit_byte_overview(inputstring, 10)
        
        result = utilities.generate_bit_byte_overview(inputstring, 4, True)
        print("\n\nOutput from generate_bit_byte_overview('1' + ' '*63, 4, True):")   
        print(result)  # Check the output manually

    def testWrongInputValue(self):
        self.assertRaises(ValueError, utilities.generate_bit_byte_overview, '001')


class TestGenerateCanIntegerOverview(unittest.TestCase):

    def test_known_values(self):
        result = utilities.generate_can_integer_overview(1)
        print('\n\nOutput from generate_can_integer_overview(1):')   # Check the output manually
        print(result)


class TestBytesToInt(unittest.TestCase):

    knownValues = (
        (b"\x00", 0),
        (b"\x01", 72057594037927936),
        (b"\x01\x00\x00\x00\x00\x00\x00\x00", 72057594037927936),
        (b"\x00\x00\x00\x00\x00\x00\x00\x01", 1),
        (b"\x00\x00\x00\x00\x00\x00\x00\x10", 16),
        (b"\x00\x00\x00\x00\x00\x00\x00\xFF", 255),
        (b"\x00\x00\x00\x00\x00\x00\x01\x00", 256),
        (b"\x00\x00\x00\x00\x00\x01\x00\x00", 65536),
        (b"\x00\x00\x00\x00\x01\x00\x00\x00", 16777216),
        (b"\x00\x00\x00\x01\x00\x00\x00\x00", 4294967296),
    )

    def testKnownValues(self):
        for inputvalue, knownresult in self.knownValues:
            result = utilities.can_bytes_to_int(inputvalue)
            self.assertEqual(result, knownresult)


class TestIntToBytes(unittest.TestCase):
    knownValues = (
        (1, 0, b""),
        (1, 1, b"\x00"),
        (1, 2, b"\x00\x00"),
    )

    def testKnownValues(self):
        for inputvalue, number_of_bytes, knownresult in self.knownValues:
            result = utilities.int_to_can_bytes(number_of_bytes, inputvalue)
            self.assertEqual(result, knownresult)


class TestTwosComplement(unittest.TestCase):

    # Known values from https://en.wikipedia.org/wiki/Two%27s_complement
    knownValues = (
        (-4, 3, 4),
        (-3, 3, 5),
        (-2, 3, 6),
        (-1, 3, 7),
        (0, 3, 0),
        (1, 3, 1),
        (2, 3, 2),
        (3, 3, 3),
        (-128, 8, 128),
        (-127, 8, 129),
        (-126, 8, 130),
        (-2, 8, 254),
        (-1, 8, 255),
        (0, 8, 0),
        (1, 8, 1),
        (2, 8, 2),
        (126, 8, 126),
        (127, 8, 127),
    )

    def testKnownValues(self):
        for inputvalue, numberofbits, knownresult in self.knownValues:
            result = utilities.twos_complement(inputvalue, numberofbits)
            self.assertEqual(result, knownresult)

    def testWrongInputValue(self):
        self.assertRaises(exceptions.CanException, utilities.twos_complement, 4, 3)
        self.assertRaises(exceptions.CanException, utilities.twos_complement, -5, 3)
        self.assertRaises(exceptions.CanException, utilities.twos_complement, 128, 8)
        self.assertRaises(exceptions.CanException, utilities.twos_complement, -129, 8)


class TestFromTwosComplement(unittest.TestCase):

    knownValues = TestTwosComplement.knownValues

    def testKnownValues(self):
        for knownresult, numberofbits, inputvalue in self.knownValues:
            result = utilities.from_twos_complement(inputvalue, numberofbits)
            self.assertEqual(result, knownresult)

    def testWrongInputValue(self):
        self.assertRaises(exceptions.CanException, utilities.from_twos_complement, 8, 3)
        self.assertRaises(exceptions.CanException, utilities.from_twos_complement, -1, 3)
        self.assertRaises(exceptions.CanException, utilities.from_twos_complement, 256, 8)
        self.assertRaises(exceptions.CanException, utilities.from_twos_complement, -1, 8)


class TestTwosComplementSanity(unittest.TestCase):

    def testSanity(self):
        for bits in range(1, 14):
            for inputvalue in range(2 ** bits):
                result = utilities.twos_complement(utilities.from_twos_complement(inputvalue, bits), bits)
                self.assertEqual(result, inputvalue)


class TestSplitSeconds(unittest.TestCase):

    knownValues = (
        (0, 0, 0),
        (0.000001, 0, 1),
        (0.001, 0, 1000),
        (0.02, 0, 20000),
        (0.25, 0, 250000),
        (0.33, 0, 330000),
        (.9, 0, 900000),
        (.99, 0, 990000),
        (1.0, 1, 0),
        (1, 1, 0),
        (1.25, 1, 250000),
        (99.99, 99, 990000),
        (100000.1, 100000, 100000),
    )

    def testKnownValues(self):
        USECONDS_DELTA = 1
        for inputvalue, known_seconds_full, known_useconds in self.knownValues:
            result_seconds_full, result_useconds = utilities.split_seconds_to_full_and_part(inputvalue)

            self.assertEqual(result_seconds_full, known_seconds_full)
            self.assertLessEqual(result_useconds, known_useconds + USECONDS_DELTA)
            self.assertGreaterEqual(result_useconds, known_useconds - USECONDS_DELTA)

    def testWrongInputValue(self):
        self.assertRaises(exceptions.CanException, utilities.split_seconds_to_full_and_part, -0.001)
        self.assertRaises(exceptions.CanException, utilities.split_seconds_to_full_and_part, -1)
        self.assertRaises(exceptions.CanException, utilities.split_seconds_to_full_and_part, -1.0)
        self.assertRaises(exceptions.CanException, utilities.split_seconds_to_full_and_part, -1000)


class TestCheckFrameId(unittest.TestCase):

    def testKnownValues(self):
        utilities.check_frame_id_and_format(0, 'standard')
        utilities.check_frame_id_and_format(0, 'extended')
        utilities.check_frame_id_and_format(7, 'standard')
        utilities.check_frame_id_and_format(19, 'extended')
        utilities.check_frame_id_and_format(0x7FF, 'standard')
        utilities.check_frame_id_and_format(0x1FFFFFFF, 'extended')

    def testWrongInputValue(self):
        self.assertRaises(exceptions.CanException, utilities.check_frame_id_and_format, None, 'standard')
        self.assertRaises(exceptions.CanException, utilities.check_frame_id_and_format, None, 'extended')
        self.assertRaises(exceptions.CanException, utilities.check_frame_id_and_format, -1, 'standard')
        self.assertRaises(exceptions.CanException, utilities.check_frame_id_and_format, -1, 'extended')
        self.assertRaises(exceptions.CanException, utilities.check_frame_id_and_format, 0x800, 'standard')
        self.assertRaises(exceptions.CanException, utilities.check_frame_id_and_format, 0x20000000, 'extended')

    def testWrongInputType(self):
        self.assertRaises(exceptions.CanException, utilities.check_frame_id_and_format, "ABC", 'standard')


class TestGetBusvalueFromBytes(unittest.TestCase):

    knownValues = (
        (b"\x00\x00\x00\x00\x00\x00\x00\x01", 'big', 8, 56, 1),
        (b"\x00\x00\x00\x00\x00\x00\x00\x06", 'big', 4, 56, 6),
        (b"\x00\x00\x00\x00\x00\x00\x00\xFF", 'big', 8, 56, 255),
        (b"\x00\x00\x00\x00\x00\x00\xFF\xFF", 'big', 16, 56, 65535),
        (b"\x00\x00\x00\x00\x00\x00\x00\x01", 'big', 1, 56, 1),
        (b"\x00\x00\x00\x00\xFF\x00\x00\x00", 'big', 8, 32, 255),
        (b"\x00\x00\x00\xFF\xFF\x00\x00\x00", 'big', 16, 32, 65535),
        (b"\x00\x00\x00\xFF\xFF\x00\x00\x00", 'big', 16, 32, 65535),
        (b"\x00\x00\x00\x00\x00\x00\x00\x01", 'little', 8, 56, 1),
        (b"\x00\x00\x00\x00\x00\x00\x00\xFF", 'little', 8, 56, 255),
        (b"\x00\x00\x00\x00\x00\x00\xFF\xFF", 'little', 16, 48, 65535),
        (b"\x00\x00\x00\x00\x00\x00\x00\x01", 'little', 1, 56, 1),
        (b"\x00\x00\x00\x00\xFF\x00\x00\x00", 'little', 8, 32, 255),
        (b"\xFF\x00\x00\x00\x00\x00\x00\x00", 'little', 8, 0, 255),
        (b"\x00\x00\x00\x02\x01\x00\x00\x00", 'little', 16, 24, 256 + 2),
    )

    def testKnownValues(self):
        for input_bytes, endianness, numberofbits, startbit, known_busvalue in self.knownValues:
            result_busvalue = utilities.get_busvalue_from_bytes(input_bytes, endianness, numberofbits, startbit)
            self.assertEqual(result_busvalue, known_busvalue)

        # These bytes have also other bits set.
        self.assertEqual(utilities.get_busvalue_from_bytes(b"\x00\x00\x00\xFF\xFF\x00\x00\x00", 'big', 8, 32), 255)
        self.assertEqual(utilities.get_busvalue_from_bytes(b"\x00\x00\x00\xFF\xFF\x00\x00\x00", 'big', 16, 32), 65535)


class TestGetShiftedvalueFromBusvalue(unittest.TestCase):

    knownValues = TestGetBusvalueFromBytes.knownValues

    def testKnownValues(self):
        for known_bytes, endianness, numberofbits, startbit, input_busvalue in self.knownValues:
            result_shiftedvalue = utilities.get_shiftedvalue_from_busvalue(input_busvalue, endianness, numberofbits, startbit)
            self.assertEqual(result_shiftedvalue, utilities.can_bytes_to_int(known_bytes))


if __name__ == '__main__':

        # Run all tests #
    unittest.main()

        # Run a single test #
    # suite = unittest.TestSuite()
    # suite.addTest(TestGetShiftedvalueFromBusvalue("testKnownValues"))
    # unittest.TextTestRunner(verbosity=2).run(suite)
