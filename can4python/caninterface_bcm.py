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

import errno
import socket
import struct
import sys

from . import canframe
from . import constants
from . import exceptions
from . import utilities


class SocketCanBcmInterface():
    """
    A Linux SocketCAN interface, using the Broadcast Manager (BCM) in the Linux kernel.
    
    Args:
      interfacename (str): For example 'vcan0' or 'can1'
      timeout (numerical or None): Timeout value in seconds receiving BCM messages from the kernel. Defaults
        to None (blocking).

    Raises:
      CanException: For interface problems. See :exc:`.CanException`.
      CanTimeoutException: At timeout. See :exc:`.CanTimeoutException`.

    """

    def __init__(self, interfacename, timeout=None):
        assert sys.version_info >= (3, 4, 0), "Python version 3.4 or later required for using SocketCAN BCM!"

        self._interfacename = str(interfacename)
        self._socket = socket.socket(socket.PF_CAN, socket.SOCK_DGRAM, socket.CAN_BCM)
        try:
            self._socket.settimeout(timeout)
            self._socket.connect((self._interfacename,))
        except (ValueError, TypeError):
            self.close()
            raise exceptions.CanException("Wrong timeout value for CAN interface {}: {!r}".format(
                                          self._interfacename, timeout))
        except OSError:
            self.close()
            raise exceptions.CanException("Could not open CAN interface {}".format(self._interfacename))

    def __repr__(self):
        return "SocketCan BCM interface: {}".format(self._interfacename)

    @property
    def interfacename(self):
        """Get the interface name (read-only). The interface name is set in the constructor."""
        return self._interfacename

    def close(self):
        """Close the socket"""
        self._socket.close()
    
    def recv_next_frame(self):
        """Receive one CAN frame.

        Returns a :class:`.CanFrame` object.

        """
                # Receive BCM message
        try:
            raw_message, address = self._socket.recvfrom(constants.MAX_NUMBER_OF_BYTES_FROM_BCM)
        except socket.timeout:
            raise exceptions.CanTimeoutException("Timeout when reading BCM message from CAN interface {}".format(
                                                 self._interfacename))
        except OSError as e:
            if e.errno == errno.EBADF:  # 9 on Linux
                raise exceptions.CanException("The BCM socket seems to be closed. CAN interface: {}".format(
                                              self._interfacename))
            elif e.errno == errno.ENETDOWN:  # 100 on Linux
                raise exceptions.CanException("The CAN interface {} seems to be down.".format(
                                              self._interfacename))
            raise

                # Parse BCM header
        try:
            opcode, flags, ival1_count, ival1, ival2, frame_id, frame_format, number_of_bcm_frames = \
                _parse_bcm_header(raw_message[0:constants.SIZE_BCM_HEADER])
        except IndexError:
            raise exceptions.CanException("Too short BCM header received: {!r}".format(raw_message))
        except Exception as e:
            raise exceptions.CanException("Malformed BCM header received: {!r}. Exception: {r}".format(
                                          raw_message, e))

        if opcode != socket.CAN_BCM_RX_CHANGED:
            raise exceptions.CanException("Wrong BCM message opcode: {!r}".format(raw_message))

                # Extract CAN frame
        try:
            raw_frame = raw_message[constants.SIZE_BCM_HEADER:
                                    constants.SIZE_BCM_HEADER + constants.SIZE_CAN_RAWFRAME]
        except IndexError:
            raise exceptions.CanException("Too short BCM frame received: {!r}".format(raw_message))

        return canframe.CanFrame.from_rawframe(raw_frame)
        
    def send_frame(self, input_frame):
        """Send a single CAN frame (a :class:`.CanFrame` object)"""
        try:
            header = _build_bcm_header(socket.CAN_BCM_TX_SEND,
                                       flags=0,
                                       interval=0,
                                       frame_id=input_frame.frame_id,
                                       frame_format=input_frame.frame_format,
                                       number_of_bcm_frames=1)
        except AttributeError:
            raise exceptions.CanException("The input_frame is wrong: {!r}".format(input_frame))
        self._send_via_socket(header + input_frame.get_rawframe())

    def setup_periodic_send(self, input_frame, interval=None, restart_timer=True):
        """Setup periodic transmission for a frame ID.

        Args:
          input_frame (:class:`.CanFrame` object): The frame (including data and frame ID) to send periodically.
          interval (float or None): Interval between consecutive transmissions (in milliseconds). Defaults
            to None (do not update the timing information).
          restart_timer (bool): Start or restart the transmission timer. Defaults to True. Set
            this to false if you just would like to update the data to be sent, but not force
            reset of the transmission timer.

        """
        # Possibly use the TX_ANNOUNCE flag to emit data changes immediately (does not affect timer cycle)

        flags = 0
        if interval is None:
            interval = 0
        else:
            try:
                float(interval)
            except ValueError:
                raise exceptions.CanException("Wrong interval type: {!r}".format(interval))
            if interval < 0:
                raise exceptions.CanException("Wrong interval: {!r}".format(interval))
            flags |= constants.BCM_FLAG_SETTIMER
        restart_timer = bool(restart_timer)
        if restart_timer:
            flags |= constants.BCM_FLAG_STARTTIMER
        try:
            header = _build_bcm_header(socket.CAN_BCM_TX_SETUP,
                                       flags=flags,
                                       interval=interval,
                                       frame_id=input_frame.frame_id,
                                       frame_format=input_frame.frame_format,
                                       number_of_bcm_frames=1)
        except AttributeError:
            raise exceptions.CanException("The input_frame is wrong: {!r}".format(input_frame))
        self._send_via_socket(header + input_frame.get_rawframe())

    def stop_periodic_send(self, frame_id, frame_format=constants.CAN_FRAMEFORMAT_STANDARD):
        """Stop the periodic transmission for this frame_id.

        Args:
          frame_id (int): Frame ID
          frame_format (str): Frame format. Should be ``'standard'`` or ``'extended'``. Defaults to standard frame format.

        """
        utilities.check_frame_id_and_format(frame_id, frame_format)
        header = _build_bcm_header(socket.CAN_BCM_TX_DELETE,
                                   flags=0,
                                   interval=0,
                                   frame_id=frame_id,
                                   frame_format=frame_format,
                                   number_of_bcm_frames=0)
        self._send_via_socket(header)

    def setup_reception(self, frame_id, frame_format=constants.CAN_FRAMEFORMAT_STANDARD,
                        min_interval=None, data_mask=None):
        """Setup reception for this frame_id (pretty much subscribe).

        Args:
          frame_id (int): Frame ID
          frame_format (str): Frame format. Should be ``'standard'`` or ``'extended'``. Defaults to
              standard frame format.
          min_interval (float or None): Minimum interval between received frames (in milliseconds). Useful for
              throttling rapid data streams. Defaults to None (no throttling). A min_interval of 0 corresponds to
              no throttling.
          data_mask (bytes or None): Enable filtering on data changes. The mask is bytes object (length 8 bytes). Set
              the corresponding bits to 1 to detect data change in that location. Defaults to None (data is not studied
              for changes, all incoming frames are given to the user).

        """
        utilities.check_frame_id_and_format(frame_id, frame_format)

        flags = 0
        if min_interval is None:
            min_interval = 0
        else:
            if min_interval < 0:
                raise exceptions.CanException("Wrong min_interval: {!r}".format(min_interval))
            elif min_interval > 0:
                flags |= constants.BCM_FLAG_SETTIMER

        if data_mask is None:
            flags |= constants.BCM_FLAG_RX_FILTER_ID  # All frames with this particular ID will be received.
            masking_frame = canframe.CanFrame(frame_id,
                                              constants.NULL_BYTE * constants.MAX_NUMBER_OF_CAN_DATA_BYTES,
                                              frame_format)
        else:
            if len(data_mask) != constants.MAX_NUMBER_OF_CAN_DATA_BYTES:
                raise exceptions.CanException("Wrong data_mask: {!r}".format(data_mask))
            flags |= constants.BCM_FLAG_RX_CHECK_DLC  # Detect also changes in DLC
            masking_frame = canframe.CanFrame(frame_id, data_mask, frame_format)

        header = _build_bcm_header(socket.CAN_BCM_RX_SETUP,
                                   flags=flags,
                                   interval=min_interval,
                                   frame_id=frame_id,
                                   frame_format=frame_format,
                                   number_of_bcm_frames=1)
        self._send_via_socket(header + masking_frame.get_rawframe())

    def stop_reception(self, frame_id, frame_format=constants.CAN_FRAMEFORMAT_STANDARD):
        """Disable the reception for this frame_id.

        Args:
          frame_id (int): Frame ID
          frame_format (str): Frame format. Should be ``'standard'`` or ``'extended'``. Defaults to standard frame format.

        """
        utilities.check_frame_id_and_format(frame_id, frame_format)
        header = _build_bcm_header(socket.CAN_BCM_RX_DELETE,
                                   flags=0,
                                   interval=0,
                                   frame_id=frame_id,
                                   frame_format=frame_format,
                                   number_of_bcm_frames=0)
        self._send_via_socket(header)

    def _send_via_socket(self, input_bytes):
        """Send data on the object's socket. Handles OSError.

        Args:
          input_bytes (byte): Data to send

        """
        try:
            self._socket.send(input_bytes)
        except OSError as e:
            if e.errno == errno.EBADF:  # 9 on Linux
                template = "Could not send CAN BCM message on interface {}. The BCM socket seems to be closed."
                raise exceptions.CanException(template.format(self._interfacename))
            elif e.errno == errno.ENETDOWN:  # 100 on Linux
                template = "Could not send CAN BCM message on interface {}. The CAN interface seems to be down."
                raise exceptions.CanException(template.format(self._interfacename))
            elif e.errno == errno.EINVAL:  # 22 on Linux
                template = "Could not send CAN BCM message on interface {}. Linux kernel SocketCAN is protesting. " + \
                           "You are probably referring to a non-existing frame."
                raise exceptions.CanNotFoundByKernelException(template.format(self._interfacename))
            raise

def _build_bcm_header(opcode, flags, interval, frame_id, frame_format, number_of_bcm_frames):
    """
    Build a BCM message header.

    Args:
      opcode (int): Command to the BCM
      flags (int): Flags to the BCM
      interval (float): Timing interval in milliseconds
      frame_id (int): Frame ID.
      frame_format (str):  Frame format. Should be ``'standard'`` or ``'extended'``
      number_of_bcm_frames (int): Number of attached raw frames to the header.

    Returns the header as bytes (length 56 bytes)

    Note that 'interval' is the ival2 in Linux kernel documentation.

    """
    frame_id_std_ext = frame_id
    if frame_format == constants.CAN_FRAMEFORMAT_EXTENDED:
        frame_id_std_ext |= constants.CAN_MASK_EXTENDED_FRAME_BIT
    interval_s = interval / constants.MILLISECONDS_PER_SECOND

    ival1_count = 0
    ival1 = 0
    ival1_seconds, ival1_useconds = utilities.split_seconds_to_full_and_part(ival1)
    ival2_seconds, ival2_useconds = utilities.split_seconds_to_full_and_part(interval_s)

    return struct.pack(constants.FORMAT_BCM_HEADER,
                       opcode,
                       flags,
                       ival1_count,
                       ival1_seconds, ival1_useconds,
                       ival2_seconds, ival2_useconds,
                       frame_id_std_ext,
                       number_of_bcm_frames)


def _parse_bcm_header(header):
    """Parse a BCM message header.

    Args:
      header (bytes): BCM header. Should have a length of 56 bytes.

    Returns the tuple
    (opcode, flags, ival1_count, ival1, ival2, frame_id, frame_format, number_of_bcm_frames)

    """
    opcode, flags, ival1_count, ival1_seconds, ival1_useconds, ival2_seconds, ival2_useconds, \
        frame_id_std_ext, number_of_bcm_frames = struct.unpack(constants.FORMAT_BCM_HEADER, header)

    ival1 = (ival1_seconds + ival1_useconds / constants.MICROSECONDS_PER_SECOND) * constants.MILLISECONDS_PER_SECOND
    ival2 = (ival2_seconds + ival2_useconds / constants.MICROSECONDS_PER_SECOND) * constants.MILLISECONDS_PER_SECOND

    frame_id = frame_id_std_ext & constants.CAN_MASK_ID_ONLY
    frame_format = constants.CAN_FRAMEFORMAT_EXTENDED if frame_id_std_ext & constants.CAN_MASK_EXTENDED_FRAME_BIT \
        else constants.CAN_FRAMEFORMAT_STANDARD

    return opcode, flags, ival1_count, ival1, ival2, frame_id, frame_format, number_of_bcm_frames
