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

from . import constants
from . import utilities
from . import exceptions

SYMBOL_LEAST_SIGNIFICANT_BIT = "L"
SYMBOL_MOST_SIGNIFICANT_BIT = "M"
SYMBOL_OTHER_VALID_BIT = "X"
    
    
class CanSignalDefinition():
    """A class for describing a CAN signal definition (not the value of the signal).
    
    Attributes:
      signalname (str): Signal name
      unit (str): Unit for the value. Defaults to ``''``.
      comment (str): A human-readable comment. Defaults to ``''``.

    Raises:
      CanException: For wrong startbit, endianness etc. See :exc:`.CanException`.

    .. warning::

       When setting the :attr:`numberofbits` attribute, then the attributes :attr:`endianness`
       and :attr:`startbit` must already be correct. Otherwise the error-checking mechanism might raise an error.

       Also, the :attr:`minvalue`, :attr:`maxvalue` and :attr:`defaultvalue` should be within the limits
       defined by :attr:`numberofbits`, :attr:`scalingfactor`, :attr:`signaltype` etc.

    .. note::

       The byte order in a CAN frame is ``0 1 2 3 4 5 6 7`` (left to right)

       The byte ``0`` in the CAN frame is sent first.

       Bit order (significance) is decreasing from left to right. So in a byte, the rightmost bit is least significant.

    Bit numbering in the CAN frame (standard bit numbering):

      * In the first byte the least significant bit (rightmost, value 1) is named ``0``,
        and the most significant bit (leftmost, value 128) is named ``7``.
      * In next byte, the least significant bit is named ``8`` etc.
    
    This results in this bit numbering for the CAN frame::
    
        7,6,5,4,3,2,1,0  15,14,13,12,11,10,9,8  23,22,21,20,19,18,17,16  31,30,29,28,27,26,25,24 etc.
        Byte0            Byte1                  Byte2                    Byte3

    .. note::

       The start bit is given for the least significant bit in the signal, in standard bit numbering.

    When a signal spans several bytes in the frame, the CAN frame can be constructed in two ways:

      * In big-endian (Motorola, Network) byte order, the most significant byte is sent first.
      * In little-endian (Intel) byte order, the least significant byte is sent first.

    For example, an integer ``0x0102030405060708`` can be transmitted as big-endian or little-endian:

      * Big-endian (most significant byte first): ``01 02 03 04 05 06 07 08``
      * Little-endian (least significant byte first): ``08 07 06 05 04 03 02 01``

    .. note::

       If the signal is fitting into a single byte (not crossing any byte borders), there is
       no difference between big and little endian.

    There is an alternate overall bit numbering scheme, known as "backwards" bit numbering.

    Other variants (not used in this software):

        * Startbit is sometimes given as the most significant bit.

    """
    def __init__(self, signalname, startbit, numberofbits, scalingfactor=1, valueoffset=0, defaultvalue=None,
                 unit="", comment="", minvalue=None, maxvalue=None,
                 endianness=constants.LITTLE_ENDIAN, signaltype=constants.CAN_SIGNALTYPE_UNSIGNED):

        # Properties #
        self.endianness = endianness
        self.signaltype = signaltype
        self.startbit = startbit
        self.numberofbits = numberofbits  # Must be set after startbit and after signaltype
        self.scalingfactor = scalingfactor
        self.valueoffset = valueoffset
        self.minvalue = minvalue
        self.maxvalue = maxvalue

        if defaultvalue is None:
            defaultvalue = valueoffset
        self.defaultvalue = defaultvalue

        # Plain attributes #
        self.signalname = str(signalname)
        self.unit = str(unit)
        self.comment = str(comment)

    @property
    def endianness(self):
        """
        *str* ``'big'`` or ``'little'``. Defaults to using little endian (as the KCD file
        format defaults to little endian).

        """
        return self._endianness

    @endianness.setter
    def endianness(self, value):
        if value not in [constants.LITTLE_ENDIAN, constants.BIG_ENDIAN]:
                raise exceptions.CanException("endianness is wrong. Given: {!r}".format(value))
        self._endianness = value

    @property
    def signaltype(self):
        """
        *str* Should be ``'unsigned'``, ``'signed'``, ``'single'`` or ``'double'``.
        (The last two are floats). Defaults to using unsigned signal type.

        """
        return self._signaltype

    @signaltype.setter
    def signaltype(self, value):
        if value not in [constants.CAN_SIGNALTYPE_UNSIGNED, constants.CAN_SIGNALTYPE_SIGNED,
                         constants.CAN_SIGNALTYPE_SINGLE, constants.CAN_SIGNALTYPE_DOUBLE]:
            raise exceptions.CanException("signaltype is wrong. Given: {!r}".format(value))
        self._signaltype = value

    @property
    def scalingfactor(self):
        """
        *numerical* Scaling factor. Multiply with this value when extracting the signal from the CAN frame.
        Defaults to ``1``. Should be positive.

        """
        return self._scalingfactor

    @scalingfactor.setter
    def scalingfactor(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError) as _:
            raise exceptions.CanException("scalingfactor should be numerical. Given: {!r}".format(value))
        if value <= 0:
            raise exceptions.CanException("scalingfactor should be positive. Given: {!r}".format(value))
        self._scalingfactor = value

    @property
    def valueoffset(self):
        """
        *numerical* Offset. Add this value when extracting the signal from the CAN frame. Defaults to ``0``.

        """
        return self._valueoffset

    @valueoffset.setter
    def valueoffset(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError) as _:
            raise exceptions.CanException("valueoffset should be numerical. Given: {!r}".format(value))
        self._valueoffset = value

    @property
    def startbit(self):
        """
        *int* Position of least significant bit (in the standard bit numbering). Should be in the range ``0`` to ``63``
        (inclusive).
        """
        return self._startbit

    @startbit.setter
    def startbit(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError) as _:
            raise exceptions.CanException("startbit should be an integer. Given: {!r}".format(value))
        if value < 0 or value > constants.BITS_IN_FULL_DATA - 1:
            raise exceptions.CanException("startbit is out of range. Given: {!r} (after int converstion).".
                                          format(value))
        self._startbit = value

    @property
    def defaultvalue(self):
        """
        *numerical or None*  Default value to send in frames if the signal value not is known. Defaults
        to :const:`None` (Use the 'valueoffset' value).

        """
        return self._defaultvalue

    @defaultvalue.setter
    def defaultvalue(self, value):
        self._check_signal_value_range('defaultvalue', value)
        self._defaultvalue = value

    @property
    def minvalue(self):
        """
        *numerical or None* Minimum allowed physical value. Defaults to :const:`None` (no checking is done).

        """
        return self._minvalue

    @minvalue.setter
    def minvalue(self, value):
        self._check_signal_value_range('minvalue', value)
        self._minvalue = value

    @property
    def maxvalue(self):
        """
        *numerical or None* Maximum allowed physical value. Defaults to :const:`None` (no checking is done).

        """
        return self._maxvalue

    @maxvalue.setter
    def maxvalue(self, value):
        self._check_signal_value_range('maxvalue', value)
        self._maxvalue = value

    @property
    def numberofbits(self):
        """
        *int* Number of bits in the signal. Should be in the range ``1`` to ``64`` (inclusive).

        """
        return self._numberofbits

    @numberofbits.setter
    def numberofbits(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError) as _:
            raise exceptions.CanException("numberofbits should be an integer. Given: {!r}".format(value))
        if value <= 0 or value > constants.BITS_IN_FULL_DATA:
            raise exceptions.CanException("numberofbits is out of range. Given: {!r} (after int converstion).".format(
                value))

        if self.endianness == constants.LITTLE_ENDIAN:
            stopbit = self.startbit + value - 1
            if stopbit >= constants.BITS_IN_FULL_DATA:
                raise exceptions.CanException("Wrong signal definition for little endian. Startbit: {}, bits: {}".
                                              format(self.startbit, value))
        else:  # BIG_ENDIAN
            startbit_backwards = utilities.calculate_backward_bitnumber(self.startbit)
            stopbit_backwards = startbit_backwards + value - 1
            if stopbit_backwards >= constants.BITS_IN_FULL_DATA:
                raise exceptions.CanException("Wrong signal definition for big endian. Startbit: {}, bits: {}".format(
                                              self.startbit, value))

        if self.signaltype == constants.CAN_SIGNALTYPE_SINGLE:
            if value != constants.BITS_IN_SINGLE_PRECISION_FLOAT:
                raise exceptions.CanException("Wrong number of bits for single precision float. Given: {}".format(
                    value))
        elif self.signaltype == constants.CAN_SIGNALTYPE_DOUBLE:
            if value != constants.BITS_IN_DOUBLE_PRECISION_FLOAT:
                raise exceptions.CanException("Wrong number of bits for double precision float. Given: {}".format(
                    value))
        self._numberofbits = value

    def __repr__(self):
        text = "Signal {!r} Startbit {}, bits {} (min DLC {}) {} endian, {}, scalingfactor {:1.2g}, unit: {}\n".format(
            self.signalname, self.startbit, self.numberofbits, 
            self.get_minimum_dlc(), self.endianness, self.signaltype, self.scalingfactor, self.unit)
        text += "         valoffset {:3.1f} (range {:1.1g} to {:1.1g}) min {}, max {}, default {:3.1f}.\n".format(
            self.valueoffset,
            self.get_minimum_possible_value(),
            self.get_maximum_possible_value(),
            self.minvalue,
            self.maxvalue,
            self.defaultvalue)

        MAX_COMMENT_LENGTH = 85
        if len(self.comment):
            if len(self.comment) < MAX_COMMENT_LENGTH:
                commentstring = self.comment
            else:
                commentstring = "{} ...".format(self.comment[0:MAX_COMMENT_LENGTH].replace('\n', ' ').replace('\r', ''))
            text += "         {} ".format(commentstring)
        return text
        
    def get_descriptive_ascii_art(self):
        """Create a visual indication how the signal is located in the frame_definition.
       
        Returns:
          A multi-line string.
        
        """
        tempstring, stopbit = self._get_overview_string()
        
        text = "    {!r}\n".format(self)
        text += "         Startbit normal bit numbering, least significant bit: {}\n".format(self.startbit)
        text += "         Startbit normal bit numbering, most significant bit: {}\n".format(stopbit)
        text += "         Startbit backward bit numbering, least significant bit: {}\n\n".format(
            utilities.calculate_backward_bitnumber(self.startbit))
        text += utilities.generate_bit_byte_overview(tempstring, number_of_indent_spaces=9, show_reverse_bitnumbering=True)
        return text
 
    def get_maximum_possible_value(self):
        """Get the largest value that technically could be sent with this signal.
        
        The largest integer we can store is ``2**numberofbits - 1``.
        Also the :attr:`scalingfactor`, :attr:`valueoffset` and the :attr:`signaltype` affect the result.

        This method is used to calculate the allowed ranges for the attributes :attr:`minvalue`, ':attr:`maxvalue`
        and :attr:`defaultvalue`. When using the signal, you should respect the :attr:`minvalue` and :attr:`maxvalue`.

        Returns:
          The largest possible value (*numerical*).

        See the twos_complement functions for discussion of value ranges for signed integers.

        """
        if self.signaltype == constants.CAN_SIGNALTYPE_UNSIGNED:
            max_unpacked_value = 2 ** self.numberofbits - 1

        elif self.signaltype == constants.CAN_SIGNALTYPE_SIGNED:
            max_unpacked_value = 2 ** (self.numberofbits - 1) - 1

        elif self.signaltype == constants.CAN_SIGNALTYPE_SINGLE:
            max_unpacked_value = constants.MAX_VALUE_FLOAT_SINGLE

        else:  # CAN_SIGNALTYPE_DOUBLE:
            max_unpacked_value = constants.MAX_VALUE_FLOAT_DOUBLE

        return max_unpacked_value * self.scalingfactor + self.valueoffset

    def get_minimum_possible_value(self):
        """Get the smallest value that technically could be sent with this signal.

        This method is used to calculate the allowed ranges for the attributes :attr:`minvalue`, ':attr:`maxvalue`
        and :attr:`defaultvalue`. When using the signal, you should respect the :attr:`minvalue` and :attr:`maxvalue`.

        Returns:
          The smallest possible value (*numerical*).

        """
        if self.signaltype == constants.CAN_SIGNALTYPE_UNSIGNED:
            min_unpacked_value = 0

        elif self.signaltype == constants.CAN_SIGNALTYPE_SIGNED:
            min_unpacked_value = - 2 ** (self.numberofbits - 1)

        elif self.signaltype == constants.CAN_SIGNALTYPE_SINGLE:
            min_unpacked_value = constants.MIN_VALUE_FLOAT_SINGLE

        else:  # CAN_SIGNALTYPE_DOUBLE:
            min_unpacked_value = constants.MIN_VALUE_FLOAT_DOUBLE

        return min_unpacked_value * self.scalingfactor + self.valueoffset

    def get_minimum_dlc(self):
        """Calculate the smallest number of bytes (DLC) that a frame must have, to be able to send this signal.

        Returns:
          Minimum DLC (int)

        """
        if self.endianness == constants.BIG_ENDIAN:
            bytenumber = self.startbit // constants.BITS_PER_BYTE
        else:
            stopbit = self.startbit + self.numberofbits - 1
            bytenumber = stopbit // constants.BITS_PER_BYTE
        return bytenumber + 1

    def _check_signal_value_range(self, attributename, value):
        if value is not None:
            try:
                value = float(value)
            except (TypeError, ValueError) as _:
                raise exceptions.CanException("{} should be numerical. Given: {!r}".format(attributename, value))
            lower_limit = self.get_minimum_possible_value()
            upper_limit = self.get_maximum_possible_value()
            if value < lower_limit or value > upper_limit:
                raise exceptions.CanException(
                    "{} is out of range for this signal. Given: {!r}. Allowed: {} to {}.".format(
                        attributename, value, lower_limit, upper_limit))

    def _get_overview_string(self):
        """Generate an overview string, of length 64 bits.

        Returns the tuple (outputstring, stopbit).
        """
        tempstringlist = [" "] * constants.BITS_IN_FULL_DATA
        if self.endianness == constants.LITTLE_ENDIAN:
            stopbit = self.startbit + self.numberofbits - 1
            tempstringlist[constants.BITS_IN_FULL_DATA - 1 - utilities.calculate_backward_bitnumber(stopbit)] = \
                SYMBOL_MOST_SIGNIFICANT_BIT
            tempstringlist[constants.BITS_IN_FULL_DATA - 1 - utilities.calculate_backward_bitnumber(self.startbit)] = \
                SYMBOL_LEAST_SIGNIFICANT_BIT
            if self.numberofbits > 2:
                for i in range(self.startbit + 1, stopbit):
                    tempstringlist[constants.BITS_IN_FULL_DATA - 1 - utilities.calculate_backward_bitnumber(i)] = \
                        SYMBOL_OTHER_VALID_BIT
        else:
            startbit_backward = utilities.calculate_backward_bitnumber(self.startbit)
            stopbit_backward = startbit_backward + self.numberofbits - 1
            stopbit = utilities.calculate_normal_bitnumber(stopbit_backward)

            tempstringlist[constants.BITS_IN_FULL_DATA - 1 - stopbit_backward] = SYMBOL_MOST_SIGNIFICANT_BIT
            tempstringlist[constants.BITS_IN_FULL_DATA - 1 - startbit_backward] = SYMBOL_LEAST_SIGNIFICANT_BIT
            if self.numberofbits > 2:
                for bitnumber_backward in range(startbit_backward + 1, stopbit_backward):
                    tempstringlist[constants.BITS_IN_FULL_DATA - 1 - bitnumber_backward] = SYMBOL_OTHER_VALID_BIT
        tempstring = "".join(tempstringlist)
        return tempstring, stopbit
