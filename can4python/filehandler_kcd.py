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
import xml.dom.minidom
import xml.etree.ElementTree as ElementTree

from . import cansignal
from . import canframe_definition
from . import configuration
from . import constants
from . import exceptions


class FilehandlerKcd():
    """
    File handler for the KCD file format.

    Note that only a subset of the KCD file format is implemented. These tags are read::

         * Network definition: xmlns
           * Bus: name
             * Message: id, name, length, interval, format,
               * Producer:
                 * NodeRef: id
               * Signal: endianness, length, name, offset
                 * Value: type, slope, intercept, unit, min, max
                 * Notes:

    Further, there are is some configuration information that not can be stored in a KCD file, for example message
    throttling and to only receive frames at data change.

    """

    @staticmethod
    def read(filename, busname=None):
        """Read configuration file in KCD format.

        Args:
          filename (str): Full path to the  KCD configuration file.
          busname (str or None): Which bus name in the configuration file to use when reading. Defaults
            to :const:`None` (using first alphabetically).

        Returns a :class:`.Configuration` object.

        Raises:
              CanException: When failing to read and unpack the file. See :exc:`.CanException`.

        """
        logging.info("Parsing file: {}".format(filename))
        tree = ElementTree.parse(filename)
        root = tree.getroot()

        buses = root.findall('kayak:Bus', constants.KCD_XML_NAMESPACE)
        if not buses:
            raise exceptions.CanException("Could not find any bus definition in file: {}".format(filename))

        available_busnames = sorted([x.get('name') for x in buses])
        available_busnames_string = ", ".join(available_busnames)
        logging.debug("  Found these buses: '{}' in file: {}".format(available_busnames_string, filename))

        if busname is None:
            busname = available_busnames[0]

        bus_subtree = None
        for bus in buses:
            if bus.get('name') == busname:
                bus_subtree = bus
                break
        if bus_subtree is None:
            raise exceptions.CanException("Could not find any bus named {} in file: {}. These buses are available: {}".
                                          format(busname, filename, available_busnames_string))

        logging.debug("  Using bus '{}' in file: {}".format(busname, filename))

        config = configuration.Configuration(busname=busname)
        for framedef in bus_subtree:
            frame_name = framedef.get('name')
            logging.debug("  Found framedefinition '{}' in file: {}".format(frame_name, filename))
            frame_id = int(framedef.get('id'), 16)
            frame_format = framedef.get('format', default=constants.CAN_FRAMEFORMAT_STANDARD)
            try:
                cycletime = float(framedef.get('interval'))
            except TypeError:
                cycletime = None
            try:
                frame_dlc = int(framedef.get('length'))
            except TypeError:
                frame_dlc = constants.MAX_NUMBER_OF_CAN_DATA_BYTES

            f = canframe_definition.CanFrameDefinition(frame_id, frame_name, frame_dlc, cycletime, frame_format)

            for producer in framedef.findall('kayak:Producer', constants.KCD_XML_NAMESPACE):
                for noderef in producer.findall('kayak:NodeRef', constants.KCD_XML_NAMESPACE):
                    noderef_id = noderef.get('id')
                    f.producer_ids.add(str(noderef_id))

            for signal in framedef.findall('kayak:Signal', constants.KCD_XML_NAMESPACE):
                signalname = signal.get('name')
                logging.debug("    Found signal '{}' in file: {}".format(signalname, filename))
                startbit = int(signal.get('offset'))
                numberofbits = int(signal.get('length', 1))
                endianness = signal.get('endianess', constants.LITTLE_ENDIAN)  # NOTE: the spelling

                scalingfactor = 1
                valueoffset = 0
                unit = ""
                minvalue = maxvalue = None
                signaltype = constants.CAN_SIGNALTYPE_UNSIGNED
                for val in signal.findall('kayak:Value', constants.KCD_XML_NAMESPACE):
                    scalingfactor = float(val.get('slope', 1))
                    valueoffset = float(val.get('intercept', 0))
                    unit = val.get('unit', "")
                    try:
                        minvalue = float(val.get('min'))
                    except TypeError:
                        pass
                    try:
                        maxvalue = float(val.get('max'))
                    except TypeError:
                        pass
                    signaltype = val.get('type', constants.CAN_SIGNALTYPE_UNSIGNED)

                signalcomment = ""
                for notes in signal.findall('kayak:Notes', constants.KCD_XML_NAMESPACE):
                    if notes.text is not None:
                        signalcomment += notes.text

                s = cansignal.CanSignalDefinition(signalname, startbit, numberofbits, scalingfactor, valueoffset,
                                                  unit=unit, comment=signalcomment,
                                                  minvalue=minvalue, maxvalue=maxvalue,
                                                  endianness=endianness, signaltype=signaltype)

                f.signaldefinitions.append(s)
            config.framedefinitions[f.frame_id] = f
        return config

    @staticmethod
    def write(config, filename):
        """Write configuration file in KCD frame_format (a type of XML file).

        Args:
          config (:class:`.Configuration` object): Configuration details.
          filename (str): Full path for output KCD file.

        If the attribute 'config.busname' is None, then DEFAULT_BUSNAME will  be used.

        """
        if config.busname is None:
            busname = constants.DEFAULT_BUSNAME
        else:
            busname = config.busname

        root = ElementTree.Element('NetworkDefinition', constants.KCD_XML_ROOT_ATTRIBUTES)

        ElementTree.SubElement(root, 'Document')
        bus_subtree = ElementTree.SubElement(root, 'Bus', attrib={"name": busname})

        # Frames
        for frame_id in sorted(config.framedefinitions.keys()):
            f = config.framedefinitions[frame_id]
            frame_attributes = {"name": str(f.name)}
            frame_attributes["id"] = "0x{:03X}".format(f.frame_id)
            frame_attributes["length"] = str(f.dlc)
            if f.cycletime is not None:
                frame_attributes["interval"] = str(f.cycletime)
            if f.frame_format == constants.CAN_FRAMEFORMAT_EXTENDED:
                frame_attributes["format"] = str(f.frame_format)

            m_subtree = ElementTree.SubElement(bus_subtree, "Message", attrib=frame_attributes)

            # Signals
            for s in f.signaldefinitions:
                signalattributes = {"name": s.signalname, "offset": str(s.startbit)}
                if s.numberofbits > 1:
                    signalattributes["length"] = str(s.numberofbits)
                if s.endianness == constants.BIG_ENDIAN:
                    signalattributes["endianess"] = str(s.endianness)  # Note: The spelling!

                s_subtree = ElementTree.SubElement(m_subtree, "Signal", attrib=signalattributes)

                if s.comment:
                    n_subtree = ElementTree.SubElement(s_subtree, "Notes")
                    n_subtree.text = str(s.comment)

                valueattributes = {}
                if abs(s.scalingfactor - 1) > constants.FLOAT_COMPARISON_EPSILON:
                    valueattributes["slope"] = str(s.scalingfactor)
                if abs(s.valueoffset) > constants.FLOAT_COMPARISON_EPSILON:
                    valueattributes["intercept"] = str(s.valueoffset)
                if s.signaltype != constants.CAN_SIGNALTYPE_UNSIGNED:
                    valueattributes["type"] = str(s.signaltype)
                if s.unit:
                    valueattributes["unit"] = str(s.unit)
                if s.minvalue is not None:
                    valueattributes["min"] = str(s.minvalue)
                if s.maxvalue is not None:
                    valueattributes["max"] = str(s.maxvalue)

                if len(valueattributes):
                    ElementTree.SubElement(s_subtree, "Value", attrib=valueattributes)

            # Producers
            if f.producer_ids:
                p_subtree = ElementTree.SubElement(m_subtree, "Producer")
                for producer_id in f.producer_ids:
                    nr_subtree = ElementTree.SubElement(p_subtree, "NodeRef", attrib={"id": producer_id})

        # Convert to an indented string
        xmlstring = ElementTree.tostring(root)
        reparsed_xml = xml.dom.minidom.parseString(xmlstring)
        indented_string = reparsed_xml.toprettyxml(indent="  ")

        # Save to file
        with open(filename, 'w') as f:
            f.write(indented_string)
