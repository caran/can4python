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

# CAN signal endianness
LITTLE_ENDIAN = 'little'
BIG_ENDIAN = 'big'

# CAN signal types and frame size
CAN_SIGNALTYPE_UNSIGNED = 'unsigned'
CAN_SIGNALTYPE_SIGNED = 'signed'
CAN_SIGNALTYPE_SINGLE = 'single'
CAN_SIGNALTYPE_DOUBLE = 'double'
MAX_NUMBER_OF_CAN_DATA_BYTES = 8
BITS_PER_BYTE = 8
BITS_IN_FULL_DATA = MAX_NUMBER_OF_CAN_DATA_BYTES * BITS_PER_BYTE
BITS_IN_SINGLE_PRECISION_FLOAT = 32
BITS_IN_DOUBLE_PRECISION_FLOAT = 64
BYTES_IN_SINGLE_PRECISION_FLOAT = int(BITS_IN_SINGLE_PRECISION_FLOAT / BITS_PER_BYTE)

# CAN frame formats
CAN_FRAMEFORMAT_STANDARD = 'standard'
CAN_FRAMEFORMAT_EXTENDED = 'extended'

# CAN frame ID related
MAX_CAN_FRAME_ID_STANDARD = 0x7ff
MAX_CAN_FRAME_ID_EXTENDED = 0x1fffffff
CAN_MASK_RECEIVE_ONLY_ONE_FRAMENUMBER = 0x7ff
CAN_MASK_EXTENDED_FRAME_BIT = 0x80000000
CAN_MASK_REMOTE_REQUEST_BIT = 0x40000000
CAN_MASK_ERROR_BIT = 0x20000000
CAN_MASK_ID_ONLY = 0x1FFFFFFF

# SocketCAN kernel communication formats
FORMAT_CAN_RAWFRAME = "=IB3x8s"  # CAN ID (4 bytes), DLC (1 byte), 3 pad bytes, 8 data bytes
SIZE_CAN_RAWFRAME = struct.calcsize(FORMAT_CAN_RAWFRAME)  # 16 bytes
FORMAT_BCM_HEADER = "@3I4l2I0q" # interval seconds and useconds are platform dependent, others are 'uint32'. Pad bytes are required.
SIZE_BCM_HEADER = struct.calcsize(FORMAT_BCM_HEADER)  # 56 bytes

# KCD file details
DEFAULT_BUSNAME = "Mainbus"
KCD_XML_NAMESPACE = {'kayak': 'http://kayak.2codeornot2code.org/1.0'}
KCD_XML_ROOT_ATTRIBUTES = {"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                       "xmlns": "http://kayak.2codeornot2code.org/1.0",
                       "xsi:noNamespaceSchemaLocation": "Definition.xsd"}

# BCM protocol flags. See Linux kernel include/uapi/linux/can/bcm.h
BCM_FLAG_SETTIMER = 0x0001
BCM_FLAG_STARTTIMER = 0x0002
BCM_FLAG_TX_COUNTEVT = 0x0004
BCM_FLAG_TX_ANNOUNCE = 0x0008
BCM_FLAG_TX_CP_CAN_ID = 0x0010
BCM_FLAG_RX_FILTER_ID = 0x0020
BCM_FLAG_RX_CHECK_DLC = 0x0040
BCM_FLAG_RX_NO_AUTOTIMER = 0x0080
BCM_FLAG_RX_ANNOUNCE_RESUME = 0x0100
BCM_FLAG_TX_RESET_MULTI_IDX = 0x0200
BCM_FLAG_RX_RTR_FRAME = 0x0400

# Number conversions
FLOAT_COMPARISON_EPSILON = 0.00001
MICROSECONDS_PER_SECOND = 1000000
MILLISECONDS_PER_SECOND = 1000

# Implementation details
FORMAT_FLOAT_DOUBLE_LITTLE_ENDIAN = "<d"  # 8 bytes
FORMAT_FLOAT_DOUBLE_BIG_ENDIAN = ">d"  # 8 bytes
FORMAT_FLOAT_SINGLE_BIG_ENDIAN = ">f"  # 4 bytes
FORMAT_DATA_LONGLONG = ">Q"  # Unsigned long long, 8 bytes
FORMAT_DATA_4BYTES_INT = ">I"  # Unsigned integer 4 bytes
NULL_BYTE = b'\x00'
MAX_NUMBER_OF_BYTES_FROM_BCM = 1024
MAX_NUMBER_OF_RAW_RECEIVE_FILTERS = 100  # Arbitrary value. Seems to work fine.
MAX_FRAME_CYCLETIME_MILLISECONDS = 60000  # Given in KCD file standard.

# CAN frame state machine values
STATUS_NONPERIODIC = 1
STATUS_PERIODIC = 2
STATUS_PERIODIC_NOT_YET_STARTED = 3

# Approximate ranges for floats
MIN_VALUE_FLOAT_SINGLE = -3.4e38
MAX_VALUE_FLOAT_SINGLE = 3.4e38
MIN_VALUE_FLOAT_DOUBLE = -1.7e308
MAX_VALUE_FLOAT_DOUBLE = 1.7e308
