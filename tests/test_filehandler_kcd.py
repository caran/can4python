#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_filehandler_kcd
----------------------------------

Tests for `filehandler_kcd` module.
"""

import contextlib
import copy
import os
import sys
import unittest

assert sys.version_info >= (3, 3, 0), "Python version 3.3 or later required!"

from can4python import canframe_definition
from can4python import configuration
from can4python import exceptions
from can4python import filehandler_kcd

try:
    from .test_configuration import FRAME_ID_SEND, TESTCONFIG1
except SystemError:  # When running this file directly
    from test_configuration import FRAME_ID_SEND, TESTCONFIG1

INPUT_FILENAME = "testfile_input.kcd"
INPUT_FILENAME_NO_BUSDEFINITION = "testfile_input_no_busdefinition.kcd"

class TestConfiguration(unittest.TestCase):

    OUTPUT_FILENAME_1 = "test_out_1_TEMPORARY.kcd"
    OUTPUT_FILENAME_2 = "test_out_2_TEMPORARY.kcd"
    OUTPUT_FILENAME_3 = "test_out_3_TEMPORARY.kcd"
    OUTPUT_FILENAME_10 = "test_out_10_TEMPORARY.kcd"

    def setUp(self):
        self.config = copy.deepcopy(TESTCONFIG1)
        parent_directory = os.path.dirname(__file__)
        self.input_filename = os.path.join(parent_directory, INPUT_FILENAME)
        self.input_filename_no_busdefinition = os.path.join(parent_directory, INPUT_FILENAME_NO_BUSDEFINITION)

    def tearDown(self):
        for filename in [self.OUTPUT_FILENAME_1,
                         self.OUTPUT_FILENAME_2,
                         self.OUTPUT_FILENAME_3,
                         self.OUTPUT_FILENAME_10]:
            with contextlib.suppress(FileNotFoundError):
                os.remove(filename)

    def testReadKcdFile(self):
        config = filehandler_kcd.FilehandlerKcd.read(self.input_filename, "Mainbus")

        self.assertEqual(config.busname, "Mainbus")

        self.assertEqual(config.framedefinitions[1].frame_id, 1)
        self.assertEqual(config.framedefinitions[1].name, 'testframedef1')
        self.assertEqual(config.framedefinitions[1].dlc, 8)
        self.assertEqual(config.framedefinitions[1].frame_format, 'standard')
        self.assertEqual(config.framedefinitions[1].cycletime, None)
        self.assertEqual(len(config.framedefinitions[1].signaldefinitions), 4)

        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].signalname, 'testsignal11')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].startbit, 56)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].numberofbits, 1)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].scalingfactor, 1)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].valueoffset, 0)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].endianness, 'little')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].signaltype, 'unsigned')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].minvalue, None)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].maxvalue, None)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].defaultvalue, 0)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].unit, "")
        self.assertEqual(config.framedefinitions[1].signaldefinitions[0].comment, "")

        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].signalname, 'testsignal12')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].startbit, 8)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].numberofbits, 16)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].scalingfactor, 1)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].valueoffset, 0)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].endianness, 'little')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].signaltype, 'unsigned')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].minvalue, 0)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].maxvalue, 100)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].defaultvalue, 0)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].unit, 'm/s')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[1].comment, "Test signal number 2")

        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].signalname, 'testsignal13')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].startbit, 24)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].numberofbits, 16)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].scalingfactor, 1)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].valueoffset, 0)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].endianness, 'little')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].signaltype, 'unsigned')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].minvalue, None)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].maxvalue, None)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].defaultvalue, 0)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].unit, '')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[2].comment, "")

        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].signalname, 'testsignal14')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].startbit, 40)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].numberofbits, 2)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].scalingfactor, 2)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].valueoffset, 20)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].endianness, 'big')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].signaltype, 'unsigned')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].minvalue, 21)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].maxvalue, 25)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].defaultvalue, 20)
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].unit, 'm/s')
        self.assertEqual(config.framedefinitions[1].signaldefinitions[3].comment, "Test signal number 4")

        fr_def = config.framedefinitions[0x12345678]
        self.assertEqual(fr_def.frame_id, 0x12345678)
        self.assertEqual(fr_def.name, 'testframedef2')
        self.assertEqual(fr_def.dlc, 4)
        self.assertEqual(fr_def.frame_format, 'extended')
        self.assertEqual(fr_def.cycletime, 50)
        self.assertEqual(len(fr_def.signaldefinitions), 1)

        self.assertEqual(fr_def.signaldefinitions[0].signalname, 'testsignal21')
        self.assertEqual(fr_def.signaldefinitions[0].startbit, 5)
        self.assertEqual(fr_def.signaldefinitions[0].numberofbits, 1)
        self.assertEqual(fr_def.signaldefinitions[0].scalingfactor, 1)
        self.assertEqual(fr_def.signaldefinitions[0].valueoffset, 0)
        self.assertEqual(fr_def.signaldefinitions[0].endianness, 'little')
        self.assertEqual(fr_def.signaldefinitions[0].signaltype, 'unsigned')
        self.assertEqual(fr_def.signaldefinitions[0].minvalue, None)
        self.assertEqual(fr_def.signaldefinitions[0].maxvalue, None)
        self.assertEqual(fr_def.signaldefinitions[0].defaultvalue, 0)
        self.assertEqual(fr_def.signaldefinitions[0].unit, "")
        self.assertEqual(fr_def.signaldefinitions[0].comment, "")

    def testReadKcdFileFaulty(self):
        self.assertRaises(exceptions.CanException,
                          filehandler_kcd.FilehandlerKcd.read, self.input_filename_no_busdefinition, None)

    def testReadKcdFileWrongBusname(self):
        self.assertRaises(exceptions.CanException,
                          filehandler_kcd.FilehandlerKcd.read, self.input_filename, "ABC")

    def testReadKcdFileNoBusnameGiven(self):
        config = filehandler_kcd.FilehandlerKcd.read(self.input_filename, None)
        self.assertEqual(config.busname, "Mainbus")

    def testWriteKcdFile(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove(self.OUTPUT_FILENAME_1)

        filehandler_kcd.FilehandlerKcd.write(self.config, self.OUTPUT_FILENAME_1)
        self.assertTrue(os.path.exists(self.OUTPUT_FILENAME_1))

        # TODO: Verify result in more detail

    def testSaveLoadedConfigurationToFile(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove(self.OUTPUT_FILENAME_2)

        config = filehandler_kcd.FilehandlerKcd.read(self.input_filename, None)
        self.assertEqual(config.busname, "Mainbus")
        filehandler_kcd.FilehandlerKcd.write(config, self.OUTPUT_FILENAME_2)
        self.assertTrue(os.path.exists(self.OUTPUT_FILENAME_2))

        # TODO: Check manually that the input and output files are similar

    def testWriteKcdFileNoBusnameGiven(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove(self.OUTPUT_FILENAME_3)

        config = configuration.Configuration()
        self.assertEqual(config.busname, None)
        filehandler_kcd.FilehandlerKcd.write(config, self.OUTPUT_FILENAME_3)

        with open(self.OUTPUT_FILENAME_3, 'r') as file:
            self.assertTrue(any("Mainbus" in line for line in file.readlines()))

    def testWriteKcdFileNoProducerGiven(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove(self.OUTPUT_FILENAME_10)

        config = configuration.Configuration()
        fr_def = canframe_definition.CanFrameDefinition(1, 'testframedef10')
        config.add_framedefinition(fr_def)

        filehandler_kcd.FilehandlerKcd.write(config, self.OUTPUT_FILENAME_10)


if __name__ == '__main__':
    unittest.main()
