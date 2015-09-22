#!/usr/bin/env python3
# 
# Manual test script for the can4python library
# Measures the (input) frame parsing speed.
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


import sys
import time
assert sys.version_info >= (3, 4, 0), "Python version 3.4 or later required!"
import can4python


############
# Settings #
############
DEFAULT_CAN_INTERFACE_NAME = 'vcan0'
NUMBER_OF_FRAMES = 10000
CAN_TIMEOUT = 5.0 # seconds


##########################
# Command line arguments #
##########################
try:
    filename = sys.argv[1]
except IndexError: 
    print("Measure parsing speed for 'can4python', using incoming CAN frames on a CAN bus.")
    print("")
    print("Usage:")
    print("   scriptname kcdfilename [CAN_interfacename]")
    sys.exit(1)
try:
    can_interface_name = sys.argv[2]
except IndexError: 
    can_interface_name = DEFAULT_CAN_INTERFACE_NAME
print("Starting. Using CAN interface: {}, timeout {:.1f} s.".format(can_interface_name, CAN_TIMEOUT))
print("Using KCD file: {}\n".format(filename))


#########################################
# Set up the CAN bus,                   #
# and verify that CAN data is available #
#########################################
canbus = can4python.CanBus.from_kcd_file(filename, can_interface_name, timeout=CAN_TIMEOUT)

print(canbus.get_descriptive_ascii_art())

print("Waiting for available CAN data before starting measurement. Reading one CAN frame ...")
signals = canbus.recv_next_signals()
print("Resulting signals:")
print(signals)


############################
# Read a lot of CAN frames #
############################
print("\nReading {} additional CAN frames ...".format(NUMBER_OF_FRAMES))
start_time = time.time()
for i in range(NUMBER_OF_FRAMES):
    signals = canbus.recv_next_signals()
total_time= time.time() - start_time


###################
# Show statistics #
###################

print("\nSignals in last frame:")
print(signals)

time_per_loop_ms = 1000 * total_time / NUMBER_OF_FRAMES
frames_per_seconds = NUMBER_OF_FRAMES / total_time
print("\nIt took {:.2f} s to unpack {} frames. (({:.2f} ms per frame, {:.1f} frames/s)".format(
    total_time, NUMBER_OF_FRAMES, time_per_loop_ms, frames_per_seconds))



