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

import math
import struct

from . import constants
from . import exceptions


def calculate_backward_bitnumber(normal_bitnumber):
    """Calculate the bit position in the "backward" numbering format.

    Args:
      normal_bitnumber (int): bit position in the standard format.

    Raises:
      CanException: For wrong bitnumber. See :exc:`.CanException`.

    Returns:
      The bit position (int) in the "backward" numbering format.

    The "backward" is a numbering scheme where the bits are numbered::

        63,62 61,60,59,58,57,56  55,54,53,52,51,50,49,48  47,46 etc
        Byte0                    Byte1                    Byte2

    In full detail::

        66665555 55555544 44444444 33333333 33222222 22221111 111111
        32109876 54321098 76543210 98765432 10987654 32109876 54321098 76543210
        Byte0    Byte1    Byte2    Byte3    Byte4    Byte5    Byte6    Byte7

    For reference, the standard bit numbering is::
    
        7,6,5,4,3,2,1,0  15,14,13,12,11,10,9,8  23,22,21,20,19,18,17,16  31,30,29,28,27,26,25,24 etc.
        Byte0            Byte1                  Byte2                    Byte3

    In full detail::

                 111111   22221111 33222222 33333333 44444444 55555544 66665555
        76543210 54321098 32109876 10987654 98765432 76543210 54321098 32109876
        Byte0    Byte1    Byte2    Byte3    Byte4    Byte5    Byte6    Byte7

    """
    if normal_bitnumber < 0:
        raise exceptions.CanException("The given normal_bitnumber is too small: {}".format(normal_bitnumber))
    if normal_bitnumber > constants.BITS_IN_FULL_DATA - 1:
        raise exceptions.CanException("The given normal_bitnumber is too large: {}".format(normal_bitnumber))
    bytenumber = normal_bitnumber // constants.BITS_PER_BYTE
    offset_in_the_byte = normal_bitnumber - bytenumber * constants.BITS_PER_BYTE  # MSbit=7, LSbit=0
    basevalue_per_byte = (constants.MAX_NUMBER_OF_CAN_DATA_BYTES - 1 - bytenumber) * constants.BITS_PER_BYTE
    return basevalue_per_byte + offset_in_the_byte


def calculate_normal_bitnumber(backward_bitnumber):
    """
    Calculate the bitnumber, from the bitnumber in backwards numbering scheme.

    This is the inverse of :func:`.calculate_backward_bitnumber`.

    Args:
      backward_bitnumber (int): The bitnumber (in backwards numbering scheme)

    Raises:
      CanException: For wrong bitnumber. See :exc:`.CanException`.

    Returns:
      The bit position (int) in the standard format.


    """
    if backward_bitnumber < 0:
        raise exceptions.CanException("The given backward_bitnumber is too small: {}".format(backward_bitnumber))
    if backward_bitnumber > constants.BITS_IN_FULL_DATA - 1:
        raise exceptions.CanException("The given backward_bitnumber is too large: {}".format(backward_bitnumber))
    bytenumber = constants.MAX_NUMBER_OF_CAN_DATA_BYTES - 1 - backward_bitnumber // constants.BITS_PER_BYTE

    # Most significant bit=7, Least significant bit=0
    offset_in_the_byte = backward_bitnumber - \
        (constants.MAX_NUMBER_OF_CAN_DATA_BYTES - 1 - bytenumber) * constants.BITS_PER_BYTE

    return offset_in_the_byte + bytenumber * constants.BITS_PER_BYTE


def generate_bit_byte_overview(inputstring, number_of_indent_spaces=4, show_reverse_bitnumbering=False):
    """Generate a nice overview of a CAN frame.
    
    Args:
      inputstring (str): String that should be printed. Should be 64 characters long.
      number_of_indent_spaces (int): Size of indentation
     
    Raises:
      ValueError when *inputstring* has wrong length.

    Returns:
      A multi-line string.
    
    """
    if len(inputstring) != constants.BITS_IN_FULL_DATA:
        raise ValueError("The inputstring is wrong length: {}. {!r}".format(len(inputstring), inputstring))
    paddedstring = " ".join([inputstring[i:i + 8] for i in range(0, 64, 8)])

    indent = " " * number_of_indent_spaces
    text = indent + "         111111   22221111 33222222 33333333 44444444 55555544 66665555\n"
    text += indent + "76543210 54321098 32109876 10987654 98765432 76543210 54321098 32109876\n"
    text += indent + "Byte0    Byte1    Byte2    Byte3    Byte4    Byte5    Byte6    Byte7\n"
    text += indent + paddedstring + "\n"

    if show_reverse_bitnumbering:
        text += indent + "66665555 55555544 44444444 33333333 33222222 22221111 111111\n"
        text += indent + "32109876 54321098 76543210 98765432 10987654 32109876 54321098 76543210\n"
    return text


def generate_can_integer_overview(value):
    """Generate a nice overview of an integer, interpreted as a CAN frame/fr_def.

    Args:
      value (int): Integer representing the data of a CAN frame
     
    Returns:
      A multi-line string.

    """
    bitstring = "{:064b}".format(value)
    return generate_bit_byte_overview(bitstring)


def can_bytes_to_int(input_bytes):
    """
    Convert bytes to an integer (after padding the bytes).

    Args:
      input_bytes (bytes object): holds 0-8 bytes of data. Will be padded with empty bytes on right side.

    Returns:
      An integer corresponding to 8 bytes of data.

    Note: An input of b"\x01" will be padded to b"\x01\x00\x00\x00\x00\x00\x00\x00". This corresponds
    to an integer of 72057594037927936.

    """
    assert len(input_bytes) <= constants.MAX_NUMBER_OF_CAN_DATA_BYTES, "Too large input to can_bytes_to_int."
    framedata8bytes = bytes(input_bytes).ljust(constants.MAX_NUMBER_OF_CAN_DATA_BYTES, constants.NULL_BYTE)
    dataint = struct.unpack(constants.FORMAT_DATA_LONGLONG, framedata8bytes)[0]
    return dataint


def int_to_can_bytes(dlc, dataint):
    """
    Convert an integer to 8 bytes, and cut it from the left according to the dlc.

    Args:
      dlc (int): how many bytes it should be encoded into
      dataint (int): holds 8 bytes of data

    Returns a bytes object: 0-8 bytes of CAN data

    For example a dataint value of 1 is converted to b'\x00\x00\x00\x00\x00\x00\x00\x01'. If the dlc is given as 1,
    then the return value will be b'\x00'.

    """
    dlc = int(dlc)
    assert dlc <= constants.MAX_NUMBER_OF_CAN_DATA_BYTES, "Too large dlc given to int_to_can_bytes."
    framedata8bytes = bytes(struct.pack(constants.FORMAT_DATA_LONGLONG, dataint))
    return framedata8bytes[0:dlc]


def twos_complement(value, bits):
    """
    Calculate two's complement for a value.

    Args:
      value (int): input value (positive or negative)
      bits (int): field size

    Returns a positive integer. If in the upper part of the range, it should be interpreted as negative.

    The allowed input value range is -2**(bits-1) to +2**(bits-1)-1. For example, 8 bits gives a range of -128 to +127.

    """
    value = int(value)
    bits = int(bits)
    maxvalue = 2 ** (bits - 1) - 1
    minvalue = - 2 ** (bits - 1)
    if value > maxvalue or value < minvalue:
        raise exceptions.CanException("Wrong value for two's complement: {} Bits: {} Range: {}-{}".format(
            value, bits, minvalue, maxvalue))
    if value >= 0:
        return value
    return value + 2 ** bits


def from_twos_complement(value, bits):
    """
    Calculate the inverse (?) of two's complement for a value.

    Args:
      value (int): input value (positive)
      bits (int): field size

    Returns a positive or negative integer, in the range range is -2**(bits-1) to +2**(bits-1)-1.
    For example, 8 bits gives an output range of -128 to +127.

    """
    value = int(value)
    bits = int(bits)
    maxvalue = (2 ** bits) - 1
    if value < 0 or value > maxvalue:
        raise exceptions.CanException("Wrong value for two's complement inverse: {} Bits: {} Range: 0-{}".format(
            value, bits, maxvalue))

    max_positive_value = 2 ** (bits - 1) - 1
    if value <= max_positive_value:
        return value
    return value - 2 ** bits


def split_seconds_to_full_and_part(seconds_float):
    """Split a time value into full and fractional parts.

    Args:
      seconds_float (float): Number of seconds

    Returns (seconds_full, useconds) which both are integers. They represent the time in
        full seconds and microseconds respectively.

    """
    if seconds_float < 0:
        raise exceptions.CanException("Invalid time interval: {}".format(seconds_float))
    seconds_full = math.floor(seconds_float)
    useconds = int((seconds_float - seconds_full) * constants.MICROSECONDS_PER_SECOND)
    return seconds_full, useconds


def check_frame_id_and_format(frame_id, frame_format):
    """Check the validity of frame_id.

    Args:
      frame_id (int): frame_id to be checked
      frame_format (str): Frame format.  Should be ``'standard'`` or ``'extended'``.

    """
    if frame_format not in [constants.CAN_FRAMEFORMAT_STANDARD, constants.CAN_FRAMEFORMAT_EXTENDED]:
        raise exceptions.CanException("Wrong frame_format. Given: {!r}".format(frame_format))
    if frame_id is None:
        raise exceptions.CanException("frame_id must be given (can not be None)")
    try:
        frame_id = int(frame_id)
    except (ValueError, TypeError) as _:
        raise exceptions.CanException("frame_id should be an integer. Given: {!r}".format(frame_id))
    if frame_id < 0:
        raise exceptions.CanException("frame_id is negative. Given: {!r}".format(frame_id))
    if frame_format == constants.CAN_FRAMEFORMAT_STANDARD and frame_id > constants.MAX_CAN_FRAME_ID_STANDARD:
        raise exceptions.CanException("frame_id is too large for standard frames. Given: {!r}".format(frame_id))
    if frame_format == constants.CAN_FRAMEFORMAT_EXTENDED and frame_id > constants.MAX_CAN_FRAME_ID_EXTENDED:
        raise exceptions.CanException("frame_id is too large for extended frames. Given: {!r}".format(frame_id))


def get_busvalue_from_bytes(input_bytes, endianness, numberofbits, startbit):
    """Get the busvalue from bytes.

    Args:
      input_bytes (bytes object): up to 8 bytes of data
      endianness (str): 'big' or 'little'
      numberofbits (int): Number of bits in the signal
      startbit (int): LSB in normal bit numbering

    Returns the bus value, which is the bits interpreted as an unsigned integer. For example '0110' is interpreted
    as the unsigned integer 6. Later, it will then be converted to whatever (maybe signed or unsigned integer).

    """
    if endianness == constants.BIG_ENDIAN:
        # Calculate number of shifts to extract the signal
        # extract_shifts (int): Number of bits to be removed from least significant side.
        # Backwards bit 63 (leftmost) must be shifted 63 steps to become rightmost bit.
        extract_shifts = calculate_backward_bitnumber(startbit)
        dataint = can_bytes_to_int(input_bytes)

        # Rightshift so the interesting bits are rightmost
        shifted = dataint >> extract_shifts  # Still BIG_ENDIAN

    else:  # The input_bytes are in LITTLE_ENDIAN. Normal bit numbering.
        bytenumber_for_startbit = startbit // constants.BITS_PER_BYTE
        assert bytenumber_for_startbit < constants.MAX_NUMBER_OF_CAN_DATA_BYTES, \
            "The startbit is wrong. Given {}.".format(startbit)
        stopbit_little = startbit + numberofbits - 1
        bytenumber_for_stopbit_little = stopbit_little // constants.BITS_PER_BYTE
        assert bytenumber_for_stopbit_little < constants.MAX_NUMBER_OF_CAN_DATA_BYTES, \
            "The stopbit is wrong for LITTLE endian. Given startbit {}, numberofbits {}.".format(startbit, numberofbits)
        number_of_bytes_to_shuffle = bytenumber_for_stopbit_little - bytenumber_for_startbit + 1
        number_of_steps_to_LSBit_in_byte = startbit % constants.BITS_PER_BYTE

        reshuffled_bytes = bytearray(constants.MAX_NUMBER_OF_CAN_DATA_BYTES)

        #print("##", bytenumber_for_startbit, bytenumber_for_stopbit_little, number_of_bytes_to_shuffle, number_of_steps_to_LSBit_in_byte)

        for i in range(number_of_bytes_to_shuffle):
            bytenumber_origin = bytenumber_for_startbit + i
            bytenumber_destination = constants.MAX_NUMBER_OF_CAN_DATA_BYTES - 1 - i  # Start from right
            #print(i, bytenumber_origin, bytenumber_destination)
            reshuffled_bytes[bytenumber_destination] = input_bytes[bytenumber_origin]

        temporary_value = can_bytes_to_int(reshuffled_bytes)

        # Rightshift so the interesting bits are rightmost
        shifted = temporary_value >> number_of_steps_to_LSBit_in_byte  # Now BIG_ENDIAN

    mask = (1 << numberofbits) - 1  # Mask with ones in 'numberofbits' positions
    return shifted & mask


def get_shiftedvalue_from_busvalue(input_value, endianness, numberofbits, startbit):
    """Get the shifted value from the bus value.

    Args:
      input_value (int): Integer corresponding to the bus value.
      endianness (str): 'big' or 'little'
      numberofbits (int): Number of bits in the signal
      startbit (int): LSB in normal bit numbering

    Returns the shifted value, which later will be put into the frame using AND/OR operations together with a mask.

    Earlier the physical value has been converted to a shifted value and then to a bus value.  For example, a
    bus value input_value '0110' is interpreted as the unsigned integer 6.

    """
    encode_shifts = calculate_backward_bitnumber(startbit)  # Origin is BIG ENDIAN

    if endianness == constants.BIG_ENDIAN:
        shifted_value = input_value << encode_shifts  # Origin is BIG ENDIAN
        return shifted_value  # Still BIG_ENDIAN

    else: # Origin is BIG ENDIAN, we should convert to LITTLE_ENDIAN.
        number_of_steps_to_LSBit_in_byte = encode_shifts % constants.BITS_PER_BYTE
        bytenumber_for_startbit = startbit // constants.BITS_PER_BYTE
        stopbit_little = startbit + numberofbits - 1
        bytenumber_for_stopbit_little = stopbit_little // constants.BITS_PER_BYTE
        assert bytenumber_for_stopbit_little < constants.MAX_NUMBER_OF_CAN_DATA_BYTES, \
            "The stopbit is wrong for LITTLE endian. Given startbit {}, numberofbits {}.".format(startbit, numberofbits)
        number_of_bytes_to_shuffle = bytenumber_for_stopbit_little - bytenumber_for_startbit + 1

        partially_shifted_value = input_value << number_of_steps_to_LSBit_in_byte
        partially_shifted_bytes = int_to_can_bytes(constants.MAX_NUMBER_OF_CAN_DATA_BYTES, partially_shifted_value)
        reshuffled_bytes = bytearray(constants.MAX_NUMBER_OF_CAN_DATA_BYTES)


        for i in range(number_of_bytes_to_shuffle):
            bytenumber_origin = constants.MAX_NUMBER_OF_CAN_DATA_BYTES - 1 - i  # Start from right
            bytenumber_destination = bytenumber_for_startbit + i
            #print(i, bytenumber_origin, bytenumber_destination)
            reshuffled_bytes[bytenumber_destination] = partially_shifted_bytes[bytenumber_origin]

        return can_bytes_to_int(reshuffled_bytes)
