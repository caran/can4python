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

from . import exceptions


class Configuration():
    """
    Configuration object for the things that happen on the CAN bus. It holds frame definitions (including
    signal definitions), the busname etc. See below.

    Attributes:
      framedefinitions (dict): The keys are the frame_id (*int*) and the items are the corresponding :class:`.CanFrameDefinition` objects.
      busname (str or None): Which bus name in the configuration file to use when reading. Defaults to :const:`None` (using first alphabetically).

    """
    def __init__(self, framedefinitions=None, busname=None, ego_node_ids=None):
        if framedefinitions is None:
            self.framedefinitions = {}
        else:
            self.framedefinitions = framedefinitions
        self.busname = busname
        self.ego_node_ids = ego_node_ids

    @property
    def ego_node_ids(self):
        """
        *set of strings* Set of nodes that this program will enact. You can pass it a list (it will convert to a set).

        """
        return self._ego_node_ids

    @ego_node_ids.setter
    def ego_node_ids(self, value):

        if value is None:
            self._ego_node_ids = set()
        elif isinstance(value, str):
            raise exceptions.CanException("ego_node_ids should be a list/set of strings. Given: {!r}".format(value))
        else:
            try:
                self._ego_node_ids = set(map(str, value))
            except TypeError:
                raise exceptions.CanException("ego_node_ids should be a list/set of strings. Given: {!r}".format(value))

    def __repr__(self):
        return "CAN configuration object. Busname '{}', having {} frameIDs defined. Enacts these node IDs: {}".format(
            self.busname, len(self.framedefinitions), " ".join(sorted(self.ego_node_ids)))

    def get_descriptive_ascii_art(self):
        """Display an overview of the :class:`.Configuration` object with frame definitions and signals.

        Returns:
          A multi-line string.

        """
        text = repr(self) + "\n"
        text += "    Frame definitions:\n"
        for frameID in sorted(self.framedefinitions.keys()):
            text += "\n    " + \
                    self.framedefinitions[frameID].get_descriptive_ascii_art().replace('\n', '\n    ')
        return text

    def add_framedefinition(self, framedef):
        """ Add a frame definition to the configutation.

        Args:
            framedef (:class:`.CanFrameDefinition` object): The frame definition to add.

        This is a convenience function. These two alternatives are equal::

            myconfig.add_framedefinition(framedef1)
            myconfig.framedefinitions[framedef1.frame_id] = framedef1

        """
        self.framedefinitions[framedef.frame_id] = framedef

    def set_throttle_times(self, inputdict):
        """ Set throttle_time for some of the framedefinitions in the configuration object.

        Args:
            inputdict (dict): The keys are the frame IDs (int) and the values are the throttle times (numerical or None) in milliseconds.

        This is a convenience function. You can instead do like this for each frame::

            myconfig.framedefinitions[myframe_id].throttle_time = mythrottletime

        """
        try:
            inputdict.items()
        except AttributeError:
            raise exceptions.CanException("The inputdict must be a dict. Given: {!r}". format(inputdict))
        for frame_id, throttle_time in inputdict.items():
            try:
                self.framedefinitions[frame_id].throttle_time = throttle_time
            except KeyError:
                raise exceptions.CanException("The frame_id given is not found in the configuration: {}".
                                              format(frame_id))

    def set_throttle_times_from_signalnames(self, inputdict):
        """ Set throttle_time for some of the framedefinitions in the configuration object (via signal names)

        Args:
         inputdict (dict): The keys are the signalnames (str) and the values are the throttle times (numerical or None) in milliseconds.

        Note that the throttle_time is set on the framedefinition holding the signalname. It will also affect other
        signals on the same frame. Setting different throttle_times to signals on the same frame will
        give an undefined result.

        This is a convenience function. You can instead do like this for each signalname::

            (first find myframe_id for a given signalname)
            myconfig.framedefinitions[myframe_id].throttle_time = mythrottletime

        """
        output_dict = {}
        # Sorting the keys to have consisting behavior in case
        # of  multiple values of throttle_time for a single framedefinition.
        try:
            signalnames = sorted(inputdict.keys())
        except AttributeError:
            raise exceptions.CanException("The inputdict must be a dict. Given: {!r}". format(inputdict))
        for signalname in signalnames:
            throttle_time = inputdict[signalname]
            frame_id = self.find_frameid_from_signalname(signalname)
            output_dict[frame_id] = throttle_time
        self.set_throttle_times(output_dict)

    def set_receive_on_change_only(self, inputlist):
        """Set receive_on_change_only for some of the framedefinitions in the configuration object.

        Args:
         inputlist (list of ints): The frame IDs that should be received only when the data has changed.

        This is a convenience function. You can instead do like this for each frame ID::

            myconfig.framedefinitions[myframe_id].receive_on_change_only = True

        """
        try:
            len(inputlist)
        except TypeError:
            raise exceptions.CanException("The inputlist must be a list. Given: {!r}". format(inputlist))
        for frame_id in inputlist:
            try:
                self.framedefinitions[frame_id].receive_on_change_only = True
            except KeyError:
                raise exceptions.CanException("The frame_id given is not found in the configuration: {} ".format(frame_id))

    def set_receive_on_change_only_from_signalnames(self, inputlist):
        """Set receive_on_change_only for some of the framedefinitions in the configuration object (via signal names).

        Args:
         inputlist (list of str): The signal names that should be received only when the data has changed.

        Note that the receive_on_change_only is set on the framedefinition holding the signalname. It will
        also affect other signals on the same frame.

        This is a convenience function. You can instead do like this for each signalname::

            (first find myframe_id for a given signalname)
            myconfig.framedefinitions[myframe_id].receive_on_change_only = True

        """
        try:
            len(inputlist)
        except TypeError:
            raise exceptions.CanException("The inputlist must be a list. Given: {!r}". format(inputlist))
        outputset = set()
        for signalname in inputlist:
            frame_id = self.find_frameid_from_signalname(signalname)
            outputset.add(frame_id)
        self.set_receive_on_change_only(outputset)

    def find_frameid_from_signalname(self, input_signalname):
        """Find which frame_id a specific signal name belongs.

        Args:
          input_signalname (str): signal name to search for.

        Returns: The frame_id (int) in which the signal is located.

        Raises:
          CanException when the given signal name not is found.

        """
        for frame_id, framedef in self.framedefinitions.items():
            for signaldef in framedef.signaldefinitions:
                if signaldef.signalname == input_signalname:
                    return framedef.frame_id
        raise exceptions.CanException("The signalname given is not found in the configuration: {}".
                                      format(input_signalname))
