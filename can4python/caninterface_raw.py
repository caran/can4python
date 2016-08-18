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
import logging
import socket
import struct

from . import canframe
from . import constants
from . import exceptions


class SocketCanRawInterface():
    """
    A Linux Socket-CAN interface, using the RAW protocol to the Linux kernel.
    
    Args:
      interfacename (str): For example 'vcan0' or 'can1'
      timeout (numerical): Timeout value in seconds for :meth:`.recv_next_signals()`. Defaults
        to None (blocking recv_next_signals).

    Raises:
      CanException: For interface problems. See :exc:`.CanException`.
      CanTimeoutException: At timeout. See :exc:`.CanTimeoutException`.

    """

    def __init__(self, interfacename, timeout=None):
        self._interfacename = str(interfacename)
        self._socket = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)

        try:
            self._socket.settimeout(timeout)
            self._socket.bind((self._interfacename,))
        except OSError:
            self.close()
            raise exceptions.CanException("Could not open CAN interface {}".format(self._interfacename))
        except (ValueError, TypeError):
            self.close()
            raise exceptions.CanException("Wrong timeout value for CAN interface {}: {!r}".format(
                                          self._interfacename, timeout))

    def __repr__(self):
        return "SocketCan raw interface: {}".format(self._interfacename)

    @property
    def interfacename(self):
        """Get the interface name (read-only). The interface name is set in the constructor."""
        return self._interfacename

    def close(self):
        """Close the socket"""
        self._socket.close()
    
    def recv_next_frame(self):
        """Receive one CAN frame. Returns a :class:`.CanFrame` object."""
        try:
            rawframe, address = self._socket.recvfrom(constants.SIZE_CAN_RAWFRAME)
            return canframe.CanFrame.from_rawframe(rawframe)
        except socket.timeout:
            raise exceptions.CanTimeoutException("Timeout when reading from CAN interface {}".format(
                                          self._interfacename))
        except OSError as e:
            if e.errno == errno.EBADF:
                raise exceptions.CanException("The CAN socket seems to be closed. CAN interface: {}".format(
                                          self._interfacename))
            elif e.errno == errno.ENETDOWN:
                raise exceptions.CanException("The CAN interface {} seems to be down.".format(
                                          self._interfacename))
            raise
        
    def send_frame(self, input_frame):
        """Send a can frame (a :class:`.CanFrame` object)"""
        try:
            self._socket.send(input_frame.get_rawframe())
        except OSError:
            raise exceptions.CanException("Could not send_frame CAN frame on interface {}".format(self._interfacename))
                
    def set_receive_filters(self, framenumbers):
        """Set the receive filters of the CAN interface (in the Linux kernel).
        
        Args:
          framenumbers (list of int): The CAN IDs to listen for.


        Uses one CAN receive filter per CAN ID.
        It is used only if listening to fewer than :data:`.MAX_NUMBER_OF_RAW_RECEIVE_FILTERS` CAN IDs,
        otherwise it is silently ignoring kernel CAN ID filering.

        To see the filters that are applied (in Ubuntu)::

          cat /proc/net/can/rcv*
          
        """
        # The filterinfo is packed in a struct:
        # filter1_id, filter1_mask, filter2_id, filter2_mask, etc where each is an interger ('I')

        if not framenumbers:
            logging.debug("Ignoring CAN filtering in the kernel, as no framenumbers are given")
            return
        if len(framenumbers) > constants.MAX_NUMBER_OF_RAW_RECEIVE_FILTERS or not framenumbers:
            logging.debug("Ignoring CAN filtering in the kernel, as {} filters are given ({} is max)".format(
                len(framenumbers), constants.MAX_NUMBER_OF_RAW_RECEIVE_FILTERS))
            return
        number_of_filters = len(framenumbers)
        filter_struct_formatstring = "={}I".format(2 * number_of_filters)

        filter_info_list = []
        for framenumber in framenumbers:
            filter_info_list.extend([framenumber, constants.CAN_MASK_RECEIVE_ONLY_ONE_FRAMENUMBER])
        filter_struct = struct.pack(filter_struct_formatstring, *filter_info_list)

        self._socket.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, filter_struct)
