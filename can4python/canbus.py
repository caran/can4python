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

import logging

from . import canframe
from . import caninterface_bcm
from . import caninterface_raw
from . import constants
from . import exceptions
from . import filehandler_kcd


class CanBus():
    """
    CAN bus abstraction.

    Uses Python 3.3 (or later) and the Linux SocketCAN interface.

    The SocketCan Broadcast Manager (BCM) handles periodic sending of CAN frames, and can throttle incoming
    CAN frames to a slower rate, or to only receive frames when the data content has changed. Python 3.4 (or later)
    is required to use the BCM.

    If you need to receive all frames, do not use the BCM.

    Args:
      config (:class:`.Configuration` object): Configuration object describing what is happening on the bus.
      interfacename (str): Name of the Linux SocketCan interface to use. For example ``'vcan0'`` or ``'can1'``.
      timeout (numerical): Timeout value in seconds for :meth:`.recv_next_signals()`. Defaults
        to :const:`None` (blocking read).
      use_bcm (bool): True if the SocketCan Broadcast manager (BCM) should be used. Defaults to False.

    """
    def __init__(self, config, interfacename, timeout=None, use_bcm=False):

        # Read-only properties
        self._configuration = config
        self._use_bcm = use_bcm

        # Initialize CAN interface
        if self._use_bcm:
            self.caninterface = caninterface_bcm.SocketCanBcmInterface(str(interfacename), timeout)
        else:
            self.caninterface = caninterface_raw.SocketCanRawInterface(str(interfacename), timeout)

        # Dict of signaldefinition objects for outgoing signals. Keys are signalnames (str).
        self._output_signaldefinition_storage = {}

        # Dict of initialized outgoing frames. Keys are signalnames (str).
        self._output_frame_storage = {}

        # Dict of framedefinitions for outgoing frames. Keys are frame_id (int).
        self._output_framedefinition_storage = {}

        # List of framedefinitions for incoming frames.
        self._input_framedefinition_storage = []

        # Dict of transmission status. Keys are frame_id (int).
        self._transmissionstatus = {}

        for frameID, framedef in self._configuration.framedefinitions.items():
            if framedef.is_outbound(config.ego_node_ids):
                self._output_framedefinition_storage[frameID] = framedef

                if framedef.cycletime in [0, None]:
                    self._transmissionstatus[framedef.frame_id] = constants.STATUS_NONPERIODIC
                else:
                    self._transmissionstatus[framedef.frame_id] = constants.STATUS_PERIODIC_NOT_YET_STARTED

                fr = canframe.CanFrame.from_empty_bytes(frameID, framedef.dlc, framedef.frame_format)
                for sigdef in framedef.signaldefinitions:
                    self._output_signaldefinition_storage[sigdef.signalname] = sigdef
                    fr.set_signalvalue(sigdef, physical_value=None)  # Use default value for signal
                    self._output_frame_storage[sigdef.signalname] = fr
            else:
                self._input_framedefinition_storage.append(framedef)

        logging.debug("Initialized {}".format(repr(self)))

    @classmethod
    def from_kcd_file(cls, filename, interfacename, timeout=None, busname=None, use_bcm=False, ego_node_ids=None):
        """
        Create a :class:`.CanBus`, using settings from a configuration file.

        This is a convenience function, to avoid creating a separate configuration object.

        Args:
          filename (str): Full path to existing configutation file, in the KCD file format.
          interfacename (str): For example ``'vcan0'`` or ``'can1'``.
          timeout (numerical): Timeout value in seconds for :meth:`.recv_next_signals()`. Defaults
            to :const:`None` (the recv_next_signals call will be blocking).
          busname (str or None): Which bus name in the messagedefinitions file to use. Defaults
            to :const:`None` (using first alphabetically).
          use_bcm (bool): True if the SocketCan Broadcast manager (BCM) should be used. Defaults to False.
          ego_node_ids (set of strings): Set of nodes that this program will enact. You can also pass it a list.

        """
        config = filehandler_kcd.FilehandlerKcd.read(filename, busname)
        config.ego_node_ids = ego_node_ids
        return cls(config, interfacename, timeout, use_bcm)

    def __repr__(self):
        protocol_string = "BCM" if self._use_bcm else "RAW"
        return "CAN bus '{}' on CAN interface: {}, having {} frameIDs defined. Protocol {}".format(
            self._configuration.busname, self.caninterface._interfacename,
            len(self._configuration.framedefinitions), protocol_string)

    @property
    def config(self):
        """Get the configuration (read-only). The configuration is set in the constructor."""
        return self._configuration

    @property
    def use_bcm(self):
        """Return True if BCM is used (read-only). Is set in the constructor."""
        return self._use_bcm

    def init_reception(self):
        """Setup the CAN frame reception.

        When using the RAW protocol, this enables filtering to reduce the input frame flow.

        It works the opposite for the BCM protocol, where it explicitly subscribes to frame IDs.

        """
        if self._use_bcm:
            for framedef in self._input_framedefinition_storage:
                mask = framedef.get_signal_mask() if framedef.receive_on_change_only else None
                self.caninterface.setup_reception(
                    framedef.frame_id, framedef.frame_format, min_interval=framedef.throttle_time, data_mask=mask)
        else:
            frame_id_list = [x.frame_id for x in self._input_framedefinition_storage]
            self.caninterface.set_receive_filters(frame_id_list)

    def recv_next_signals(self):
        """Receive one CAN frame, and unpack it to signal values.

        Returns:
          A dictionary of signal values, where the keys are the signalname (*str*) and
          the items are the values (*numerical*).

        If the frame not is defined for this :class:`.CanBus` instance, an empty dictionary is returned.

        Raises:
          CanTimeoutException: If a timeout is defined and no frame is received. See :exc:`.CanTimeoutException`.

        """
        frame = self.caninterface.recv_next_frame()
        return frame.unpack(self._configuration.framedefinitions)

    def recv_next_frame(self):
        """Receive one CAN frame. Returns a :class:`.CanFrame` object.

         Raises:
          CanTimeoutException: If a timeout is defined and no frame is received. See :exc:`.CanTimeoutException`.

        """
        return self.caninterface.recv_next_frame()

    def stop_reception(self):
        """Stop receiving, when using the BCM."""
        if not self._use_bcm:
            logging.debug("stop_receving() is not defined for the RAW backend")
            return

        for framedef in self._input_framedefinition_storage:
            try:
                self.caninterface.stop_reception(framedef.frame_id, framedef.frame_format)
            except exceptions.CanNotFoundByKernelException:
                logging.debug("This frame was probably not registered by the kernel: {}".format(framedef.frame_id))

    def send_signals(self, *args, **kwargs):
        """Send CAN signals in frames.
        
        Args:
         signals_to_send (dict): The signal values to send_frame. The keys are the signalnames (*str*),
           and the items are the values (*numerical* or *None*). If the value is *None* the default value is used.

        You can also use signal names as function arguments (keyword arguments). These are equal::

            mycanbus.send_signals({"VehicleSpeed": 70.3, "EngineSpeed": 2821})
            mycanbus.send_signals(VehicleSpeed=70.3, EngineSpeed=2821)

        The signal names must be already defined for this :class:`.CanBus` instance.

        Raises:
          CanException: When failing to set signal value etc. See :exc:`.CanException`.
        
        """
        if args:
            if isinstance(args[0], dict):
                signals_to_send = args[0]
            else:
                raise exceptions.CanException("The first argument should be a dictionary, or use keyword arguments")
        elif kwargs:
            signals_to_send = kwargs
        else:
            raise exceptions.CanException("No arguments given.")

        frames_to_send = set()
        for signalname, value in signals_to_send.items():
            try:
                signaldefinition = self._output_signaldefinition_storage[signalname]
            except KeyError:
                raise exceptions.CanException("This signalname is unknown: {}. Is it defined as outbound?".
                                              format(signalname))
            frame = self._output_frame_storage[signalname]
            frame.set_signalvalue(signaldefinition, value)  # Will raise CanException if failing
            frames_to_send.add(frame)

        if self._use_bcm:
            for frame in frames_to_send:
                status = self._transmissionstatus[frame.frame_id]

                if status == constants.STATUS_PERIODIC_NOT_YET_STARTED:
                    cycletime = self._output_framedefinition_storage[frame.frame_id].cycletime
                    self.caninterface.setup_periodic_send(frame, interval=cycletime, restart_timer=True)
                    self._transmissionstatus[frame.frame_id] = constants.STATUS_PERIODIC

                if status == constants.STATUS_PERIODIC:
                    self.caninterface.setup_periodic_send(frame, interval=None, restart_timer=False)

                else:  # non-periodic transmission
                    self.caninterface.send_frame(frame)
        else:
            for frame in frames_to_send:
                self.caninterface.send_frame(frame)

    def start_sending_all_signals(self):
        """Start sending all configured frames, when using the BCM.

        The default value for the signals are used, until updated via the :meth:`.send_signals` function.

        If you do not use this :meth:`.start_sending_all_signals` method, the periodic transmission for each frame
        will start at first :meth:`.send_signals` call.

        """
        if not self._use_bcm:
            logging.debug("start_sending_all_signals() is not defined for the RAW backend")
            return

        signals_to_send = {}
        for signalname in self._output_signaldefinition_storage.keys():
            signals_to_send[signalname] = None
        self.send_signals(signals_to_send)

    def send_frame(self, frame_to_send):
        """Send a single CAN frame.

        Args:
         frame_to_send (:class:`.CanFrame`): The frame to send.

        """
        self.caninterface.send_frame(frame_to_send)

    def stop_sending(self):
        """Stop periodic sending, when using the BCM."""
        if not self._use_bcm:
            logging.debug("stop_sending() is not defined for the RAW backend")
            return

        for frame_id, framedef in self._output_framedefinition_storage.items():
            try:
                self.caninterface.stop_periodic_send(frame_id, framedef.frame_format)
            except exceptions.CanNotFoundByKernelException:
                logging.debug("This frame was probably not registered by the kernel: {}".format(frame_id))

    def stop(self):
        """Stop periodic sending and receiving, when using the BCM."""
        self.stop_sending()
        self.stop_reception()

    def get_descriptive_ascii_art(self):
        """Display an overview of the :class:`.CanBus` object with frame definitions and signal definitions.
        
        Returns:
          A multi-line string.

        """
        text = repr(self) + "\n"
        text += "    " + self._configuration.get_descriptive_ascii_art()
        return text   
                
    def write_configuration(self, filename):
        """Write configuration to file.

         Args:
           filename (str): Full path to file with configuration.

         Saves to an XML file in the KCD file format.

         """
        filehandler_kcd.FilehandlerKcd.write(self._configuration, filename)
