==========================
Introduction to can4python
==========================

A package for handling CAN bus (Controller Area Network) signals on Linux SocketCAN, for Python 3.3 and later.

* Free software: BSD license

Web resources
-------------
* Source code on GitHub: https://github.com/caran/can4python
* Documentation: https://can4python.readthedocs.org.
* Python Package Index (PyPI): https://pypi.python.org/pypi/can4python


Features
--------
* Sends and receives CAN frames.
* Handles parsing of CAN signals from CAN frames.

..

* Uses SocketCAN for Linux.
* For Python 3.3 or later. Python 3.4 is required for some functionality.
* Implemented as pure Python files, without any external dependencies.
* Suitable for use with BeagleBone and Raspberry Pi embedded Linux boards.

..

* Configuration using the open source KCD file format.
* Throttle incoming frames to reduce frame rate.
* Filtering of incoming frames on data changes. This is done via a bit mask in the Linux kernel.
* Periodic frame transmission executed by the Linux kernel (not by Python code).

..

* Useful for showing the contents of KCD files (also those converted from DBC files).

Configuration file format
-------------------------
This CAN library uses the KCD file format for defining CAN signals and CAN messages. It is an open-source file format
for describing CAN bus relationships. See https://github.com/julietkilo/kcd for details on the format, and example
files.

The licensing of the KCD file format is, according to the web page::

    The files that are describing the format are published under the Lesser GPL license.
    The KCD format is copyrighted by Jan-Niklas Meier (dschanoeh) and Jens Krueger (julietkilo).
    According to the authors this does not imply any licensing restrictions on
    software libraries implementing the KCD file format, or on software using those libraries.

Traditionally CAN bus relationships are described in DBC files, a file format owned by Vector Informatik GmbH. There
are open source DBC-to-KCD file format converters available, for example the CANBabel tool:
https://github.com/julietkilo/CANBabel


Known limitations
-----------------
* Not all CAN functionality is implemented. 'Error frames' and 'remote request frames' are not
  handled, and CAN multiplex signals are not supported.
* Not all features of the KCD file format are implemented, for example 'Labels'.
* It is assumed that each CAN signal name only is available in a single CAN frame ID.


Dependencies
------------
The can4python package itself has no dependencies, except for Python 3.3+ running on Linux.

For tests, a virtual CAN interface ('vcan') must be installed. It is part of the Linux kernel. See the Usage page of this documentation for details.

Dependencies for testing and documentation:

=========================== ================================= ======================= ==============================
Dependency                  Description                       License                 Debian/pip package
=========================== ================================= ======================= ==============================
vcan0                       Virtual CAN bus interface         Part of Linux kernel    
coverage                    Test coverage measurement         Apache 2.0              P: coverage
texlive                     Latex library (for PDF creation)  "Knuth"                 D: texlive-full
Sphinx 1.3+                 Documentation tool                BSD 2-cl                P: sphinx
Sphinx rtd theme            Theme for Sphinx                  MIT                     P: sphinx_rtd_theme
sphinxcontrib.programoutput Capture program output for Sphinx BSD 2-cl                P: sphinxcontrib-programoutput
=========================== ================================= ======================= ==============================



Installation and usage
----------------------
See separate documentation pages.


Support
-------

The preferred way is to open a question on `Stack Overflow <http://stackoverflow.com>`_ .

Found a bug? Open an issue on Github!
