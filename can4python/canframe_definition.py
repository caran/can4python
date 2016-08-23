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
from . import exceptions
from . import utilities


class CanFrameDefinition():
    """A class for describing a CAN frame definition.

    This object defines how the signals are laid out etc, but it does not hold the value of the frame
    or the values of the signals.

    To add a :class:`.CanSignalDefinition` object to this :class:`.CanFrameDefinition` object::

       myframedef1.signaldefinitions.append(mysignal1)

    Attributes:
      name (str): Frame name
      signaldefinitions (list of CanSignalDefinition objects): Defaults to an empty list.
        See :class:`.CanSignalDefinition`.
      receive_on_change_only (bool): Receive this frame only for updated data value
        (a data bitmask will be calculated). Defaults to False.

    """
    def __init__(self, frame_id, name='', dlc=constants.MAX_NUMBER_OF_CAN_DATA_BYTES, cycletime=None,
                 frame_format=constants.CAN_FRAMEFORMAT_STANDARD):
        # Properties
        self.frame_format = frame_format  # Must be set before frame_id
        self.frame_id = frame_id
        self.dlc = dlc
        self.cycletime = cycletime
        self.throttle_time = None
        self.producer_ids = []

        # Plain attributes
        self.name = str(name)
        self.signaldefinitions = []
        self.receive_on_change_only = False


    def __repr__(self, long_text=True):
        output = "CAN frame definition. ID={0} (0x{0:03X}, {1}) '{2}', DLC={3}, cycletime {4} ms".format(
            self.frame_id, self.frame_format, self.name, self.dlc, self.cycletime, )
        output += ", producers: {!r}".format(list(self.producer_ids))
        if self.throttle_time is None:
            output += ", no throttling"
        else:             
            output += ", throttling {:.0f} ms".format(self.throttle_time)
        output += ", contains {} signals".format(len(self.signaldefinitions))
        if long_text and self.signaldefinitions:
            output += ":"
            for signal in self.signaldefinitions:
                output += "\n    {}".format(signal)
        return output

    @property
    def frame_id(self):
        """
        *int* Frame ID. Should be in the range ``0`` to ``0x7FF`` for standard frame format, or in the
        range ``0`` to ``0x1FFFFFFF`` for extended frames.
        """
        return self._id

    @frame_id.setter
    def frame_id(self, value):
        utilities.check_frame_id_and_format(value, self.frame_format)
        self._id = value

    @property
    def dlc(self):
        """
        *int* Number of bytes that should appear in the frame. Should be in the range ``0`` to
        ``8``. Default: ``8`` bytes.
        """
        return self._dlc

    @dlc.setter
    def dlc(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError) as _:
            raise exceptions.CanException("dlc should be an integer. Given: {!r}".format(value))
        if value < 0 or value > constants.MAX_NUMBER_OF_CAN_DATA_BYTES:
                raise exceptions.CanException("dlc is out of range. Given: {!r}".format(value))
        self._dlc = value

    @property
    def cycletime(self):
        """
        *numerical or None* Shortest cycle time (in milliseconds) when sending. Defaults to :const:`None`.
        """
        return self._cycletime

    @cycletime.setter
    def cycletime(self, value):
        if value is not None:
            try:
                value = int(value)
            except (ValueError, TypeError) as _:
                raise exceptions.CanException("cycletime should be numerical or None. Given: {!r}".format(value))
            if value < 0 or value > constants.MAX_FRAME_CYCLETIME_MILLISECONDS:
                raise exceptions.CanException("cycletime is out of range. Given: {!r}".format(value))
        self._cycletime = value

    @property
    def throttle_time(self):
        """
        *numerical or None* Shortest update time (in milliseconds) for this frame when receiving.
        Defaults to :const:`None` (no throttling).
        """
        return self._throttle_time

    @throttle_time.setter
    def throttle_time(self, value):
        if value is not None:
            try:
                value = int(value)
            except (ValueError, TypeError) as _:
                raise exceptions.CanException("throttle_time should be numerical or None. Given: {!r}".format(value))
            if value < 0 or value > constants.MAX_FRAME_CYCLETIME_MILLISECONDS:
                raise exceptions.CanException("throttle_time is out of range. Given: {!r}".format(value))
        self._throttle_time = value

    @property
    def frame_format(self):
        """
        *str* Frame format. Should be ``'standard'`` or ``'extended'``. Defaults to standard frame format.
        """
        return self._format

    @frame_format.setter
    def frame_format(self, value):
        if value not in [constants.CAN_FRAMEFORMAT_STANDARD, constants.CAN_FRAMEFORMAT_EXTENDED]:
            raise exceptions.CanException("Wrong frame_format. Given: {!r}".format(value))
        self._format = value

    @property
    def producer_ids(self):
        """
        *set of strings* Set of nodes (ECUs) that produce this frame. You can pass it a list (it will convert to a set).
        """
        return self._producer_ids

    @producer_ids.setter
    def producer_ids(self, value):
        if value is None:
            self._producer_ids = set()
        elif isinstance(value, str):
            raise exceptions.CanException("producer_ids should be a list/set of strings. Given: {!r}".format(value))
        else:
            try:
                self._producer_ids = set(map(str, value))
            except TypeError:
                raise exceptions.CanException("producer_ids should be a list/set of strings. Given: {!r}".format(value))

    def get_descriptive_ascii_art(self):
        """Display an overview of the frame definition with its signals.
        
        Returns:
          A multi-line string.
        """
        text = self.__repr__(long_text=False) + "\n"
        text += "    Signal details:\n"
        text += "    ---------------\n"
        for signal in self.signaldefinitions:
            text += "\n\n" + signal.get_descriptive_ascii_art()
        return text

    def get_signal_mask(self):
        """Calculate signal mask.

        Returns a bytes object (length 8 bytes). A 1 in a position indicates that there
        is an interesting signal.

        """
        output_int = 0
        for signaldef in self.signaldefinitions:

            # Generate a 64 character string describing the signal
            overviewstring, _ = signaldef._get_overview_string()

            # Look for non-empty positions in the string
            for pos, char in enumerate(overviewstring):
                if char != " ":
                    output_int |= 2 ** (constants.BITS_IN_FULL_DATA - 1 - pos)

        return utilities.int_to_can_bytes(constants.MAX_NUMBER_OF_CAN_DATA_BYTES, output_int)

    def is_outbound(self, ego_node_ids):
        """
        Args:
          ego_node_ids (list/set of strings): List of nodes that this program will enact.

        The frames with producer IDs matching some in the ego_node_ids list are
        considered outgoing/outbound frames.

        Defaults to inbound, for example if no producer_ids or ego_node_ids are given.

        Returns True if this frame is outbound (ie will be sent). Otherwise it is inbound (will be received).

        """
        if not self.producer_ids or not ego_node_ids:
            return False
        try:
            ego_node_ids = set(ego_node_ids)
        except TypeError:
            raise exceptions.CanException("Wrong ego_node_ids. Should be iterable. Given: {!r}".format(ego_node_ids))
        return bool(ego_node_ids & self.producer_ids)
