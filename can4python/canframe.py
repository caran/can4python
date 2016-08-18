# -*- coding: utf-8 -*-
#
# Author: Jonas Berg
# Copyright (c) 2015, Semcon Sweden AB
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted 
# provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the
#    following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,  this list of conditions and 
#    the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Semcon Sweden AB nor the names of its contributors may be used to endorse or 
#    promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 

import struct

from . import exceptions
from . import constants
from . import utilities


class CanFrame():
    """
    CAN frame with data. Does not know how the signals are laid out etc.

    Raises:
      CanException: For wrong frame ID. See :exc:`.CanException`.

    To find the DLC, use one of::

      len(myframe)
      len(myframe.frame_data)

    """

    def __init__(self, frame_id, frame_data, frame_format=constants.CAN_FRAMEFORMAT_STANDARD):
        # Properties #
        self.frame_format = frame_format  # Must be set before frame_id
        self.frame_id = frame_id
        self.frame_data = frame_data

    def __repr__(self):
        datastring = " ".join(["{:02X}".format(y) for y in self.frame_data]) if self.frame_data else ""
        return "CAN frame ID: {0} (0x{0:03X}, {1}) data: {2} ({3} bytes)".format(
            self.frame_id, self.frame_format, datastring, len(self.frame_data))

    def __len__(self):
        return len(self.frame_data)

    @classmethod
    def from_empty_bytes(cls, frame_id, number_of_bytes, frame_format=constants.CAN_FRAMEFORMAT_STANDARD):
        """
        Create a :class:`.CanFrame` with empty bytes.

        Args:
          frame_id (int): CAN frame ID number
          number_of_bytes (int): number of empty data bytes to initialize the frame with.
          frame_format (str): Frame format. Should be ``'standard'`` or ``'extended'``. Defaults to standard frame format.

        """
        try:
            number_of_bytes = int(number_of_bytes)
        except (ValueError, TypeError) as _:
            raise exceptions.CanException("number_of_bytes should be an integer. Given: {!r}".format(number_of_bytes))
        if (number_of_bytes > constants.MAX_NUMBER_OF_CAN_DATA_BYTES) or (number_of_bytes < 0):
                raise exceptions.CanException("Wrong number of number_of_bytes given: {!r}".format(number_of_bytes))

        framedata = constants.NULL_BYTE * number_of_bytes
        return cls(frame_id, framedata, frame_format)

    @classmethod
    def from_rawframe(cls, rawframe):
        """
        Create a :class:`.CanFrame` from a raw frame from the SocketCAN interface.

        Args:
          rawframe (bytes): 16 bytes long, includes frame ID, frame format etc

        """
        try:
            first_part, dlc, framedata8bytes = struct.unpack(constants.FORMAT_CAN_RAWFRAME, rawframe)
        except struct.error as err:
            raise exceptions.CanException("rawframe is illegal. Given: {!r}. Error: {}".format(rawframe, err))
        frame_id = first_part & constants.CAN_MASK_ID_ONLY
        frame_format = constants.CAN_FRAMEFORMAT_EXTENDED if first_part & constants.CAN_MASK_EXTENDED_FRAME_BIT \
            else constants.CAN_FRAMEFORMAT_STANDARD
        framedata = framedata8bytes[:dlc]

        # is_remote_request = bool(first_part & constants.CAN_MASK_REMOTE_REQUEST_BIT)
        # is_error_frame = bool(first_part & constants.CAN_MASK_ERROR_BIT)

        return cls(frame_id, framedata, frame_format)

    @property
    def frame_id(self):
        """
        *int* CAN frame ID number

        """
        return self._frame_id

    @frame_id.setter
    def frame_id(self, value):
        utilities.check_frame_id_and_format(value, self.frame_format)
        self._frame_id = value

    @property
    def frame_data(self):
        """
        *bytes object* 0-8 bytes of CAN data
        """
        return self._frame_data

    @frame_data.setter
    def frame_data(self, value):
        if value is None:
            raise exceptions.CanException("frame_data should not be None")
        try:
            value = bytes(value)
        except TypeError:
            raise exceptions.CanException("frame_data should be bytes. Given: {!r}".format(value))
        if len(value) > constants.MAX_NUMBER_OF_CAN_DATA_BYTES:
            raise exceptions.CanException("The frame_data has wrong length: {!r}".format(value))
        self._frame_data = value

    @property
    def frame_format(self):
        """
        *str* Frame format. Should be ``'standard'`` or ``'extended'``. Defaults to standard frame format.
        """
        return self._frame_format

    @frame_format.setter
    def frame_format(self, value):
        if value not in [constants.CAN_FRAMEFORMAT_STANDARD, constants.CAN_FRAMEFORMAT_EXTENDED]:
            raise exceptions.CanException("Wrong frame_format. Given: {!r}".format(value))
        self._frame_format = value

    def get_signalvalue(self, signaldefinition):
        """
        Extract a signal value from the frame.

        Args:
          signaldefinition (:class:`.CanSignalDefinition` object): The definition of the signal

        Returns:
            The extracted signal physical value (numerical).

        """
        if signaldefinition.signaltype == constants.CAN_SIGNALTYPE_DOUBLE:
            if signaldefinition.endianness == constants.LITTLE_ENDIAN:
                unpacked_value = struct.unpack(constants.FORMAT_FLOAT_DOUBLE_LITTLE_ENDIAN, self.frame_data)[0]
            else:
                unpacked_value = struct.unpack(constants.FORMAT_FLOAT_DOUBLE_BIG_ENDIAN, self.frame_data)[0]
        else:
            bus_value = utilities.get_busvalue_from_bytes(self.frame_data,
                                                          signaldefinition.endianness,
                                                          signaldefinition.numberofbits,
                                                          signaldefinition.startbit)

            # Unpack from signal type
            if signaldefinition.signaltype == constants.CAN_SIGNALTYPE_UNSIGNED:
                unpacked_value = bus_value
            elif signaldefinition.signaltype == constants.CAN_SIGNALTYPE_SIGNED:
                unpacked_value = utilities.from_twos_complement(bus_value, signaldefinition.numberofbits)
            else:  # CAN_SIGNALTYPE_SINGLE:
                useful_bytes = struct.pack(constants.FORMAT_DATA_4BYTES_INT, bus_value)  # Create 'bytes' of length 4
                unpacked_value = struct.unpack(constants.FORMAT_FLOAT_SINGLE_BIG_ENDIAN, useful_bytes)[0]

        physical_value = (unpacked_value * signaldefinition.scalingfactor) + signaldefinition.valueoffset

        # Limit to minvalue and maxvalue
        if signaldefinition.minvalue is not None:
            physical_value = max(signaldefinition.minvalue, physical_value)
        if signaldefinition.maxvalue is not None:
            physical_value = min(signaldefinition.maxvalue, physical_value)

        return physical_value

    def set_signalvalue(self, signaldefinition, physical_value=None):
        """
        Set a signal physical_value in the frame.
                
        Args:
          signaldefinition (:class:`.CanSignalDefinition` object): The definition of the signal
          physical_value (numerical): The physical_value (numerical) of the signal.
         
         If the physical_value not is given, the default physical_value for the *signaldefinition* is used.

        Raises:
          CanException: For wrong startbit or values. See :exc:`.CanException`.

        """
        if signaldefinition.get_minimum_dlc() > len(self):
            raise exceptions.CanException('The frame is too short to send_frame this signal. Frame: {}, signal: {}'.
                                          format(self, signaldefinition))
        if physical_value is None:
            physical_value = signaldefinition.defaultvalue

        if physical_value < signaldefinition.get_minimum_possible_value() or \
                physical_value > signaldefinition.get_maximum_possible_value():
            raise exceptions.CanException('The physical value is out of range. Value: {}, range {} to {}'.format(
                                          physical_value,
                                          signaldefinition.get_minimum_possible_value(),
                                          signaldefinition.get_maximum_possible_value()))

        # Limit to minvalue and maxvalue
        if signaldefinition.minvalue is not None:
            physical_value = max(signaldefinition.minvalue, physical_value)
        if signaldefinition.maxvalue is not None:
            physical_value = min(signaldefinition.maxvalue, physical_value)

        # Scale according to valueoffset and scalingfactor
        scaled_value = float((physical_value - signaldefinition.valueoffset) / signaldefinition.scalingfactor)

        # Shortcut for double precision floats (occupies full frame)
        if signaldefinition.signaltype == constants.CAN_SIGNALTYPE_DOUBLE:
            if signaldefinition.endianness == constants.LITTLE_ENDIAN:
                self.frame_data = struct.pack(constants.FORMAT_FLOAT_DOUBLE_LITTLE_ENDIAN, scaled_value)
            else:
                self.frame_data = struct.pack(constants.FORMAT_FLOAT_DOUBLE_BIG_ENDIAN, scaled_value)
            return

        # Encode to correct signaltype
        if signaldefinition.signaltype == constants.CAN_SIGNALTYPE_UNSIGNED:
            bus_value = int(scaled_value)
        elif signaldefinition.signaltype == constants.CAN_SIGNALTYPE_SIGNED:
            bus_value = utilities.twos_complement(int(scaled_value), signaldefinition.numberofbits)
        else:  # CAN_SIGNALTYPE_SINGLE:
            bus_value = utilities.can_bytes_to_int(
                struct.pack(constants.FORMAT_FLOAT_SINGLE_BIG_ENDIAN, scaled_value).
                rjust(constants.MAX_NUMBER_OF_CAN_DATA_BYTES, constants.NULL_BYTE))

        # Limit the size of the field to be written
        assert bus_value <= (2 ** signaldefinition.numberofbits - 1), "Trying to set too large signal value to frame."
        assert bus_value >= 0, "Trying to set too small signal value to the frame."

        bitvalues = utilities.get_shiftedvalue_from_busvalue(bus_value,
                                                             signaldefinition.endianness,
                                                             signaldefinition.numberofbits,
                                                             signaldefinition.startbit)

        raw_mask = ((1 << signaldefinition.numberofbits) - 1)  # Mask with ones in 'numberofbits' positions
        mask = utilities.get_shiftedvalue_from_busvalue(raw_mask,
                                                        signaldefinition.endianness,
                                                        signaldefinition.numberofbits,
                                                        signaldefinition.startbit)

        # Parse existing frame_data
        dataint = utilities.can_bytes_to_int(self.frame_data)
        dlc = len(self.frame_data)

        # Modify the frame_data by writing zeros to the appropriate field (using bitwise AND),
        # then writing in the relevant data (by using bitwise OR)
        dataint = (dataint & ~mask) | bitvalues

        self.frame_data = utilities.int_to_can_bytes(dlc, dataint)

    def unpack(self, frame_definitions):
        """Unpack the CAN frame, and return all signal values.
        
        Args:
          frame_definitions (dict): The keys are frame_id (int) and
            the items are :class:`.CanFrameDefinition` objects.

        Raises:
          CanException: For wrong DLC. See :exc:`.CanException`.

        Returns:
          A dictionary of signal values. The keys are the signalname (str) and the items are the values (numerical).

        If the frame not is described in the 'frame_definitions', an empty dictionary is returned.
        """
        try:
            fr_def = frame_definitions[self.frame_id]
        except KeyError:
            return {}
       
        if len(self.frame_data) != fr_def.dlc:
            raise exceptions.CanException('The received frame has wrong length: {}, Def: {}'.format(self, fr_def))
        
        outputdict = {}
        for sigdef in fr_def.signaldefinitions:
            val = self.get_signalvalue(sigdef)
            outputdict[sigdef.signalname] = val
        return outputdict
        
    def get_rawframe(self):
        """Returns a 16 bytes long 'bytes' object."""
        dlc = len(self.frame_data)
        framedata8bytes = self.frame_data.ljust(constants.MAX_NUMBER_OF_CAN_DATA_BYTES, constants.NULL_BYTE)

        # Set flag for extended frame format, if necessary
        first_part = self.frame_id
        if self.frame_format == constants.CAN_FRAMEFORMAT_EXTENDED:
            first_part |= constants.CAN_MASK_EXTENDED_FRAME_BIT
        return struct.pack(constants.FORMAT_CAN_RAWFRAME, first_part, dlc, framedata8bytes)

    def get_descriptive_ascii_art(self):
        """Create a visual indication of the frame data

        Returns:
          A multi-line string.

        """
        text = "{!r} \n".format(self)
        text += utilities.generate_can_integer_overview(utilities.can_bytes_to_int(self.frame_data))
        return text
