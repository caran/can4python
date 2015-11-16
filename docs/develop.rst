=====================
Developer information
=====================


KCD file validation
-------------------
The KCD file format is described here: https://github.com/julietkilo/kcd

There is an example file as well as a XML schema definition file (.XSD format).

Use some online XML schema validator service to make sure the imported and exported KCD files to/from can4python are valid.


TODO
----
* Handle Labels (Enums, name constants) in KCD files. For example: PowerMode='EngineRunning'
* More usage examples, also with BCM.
* Implement a get_configuration() function.
* Implement myconfiguration.get_all_signalnames()
* Verify that the 'from . import whatever' pattern is OK.
* Abstract BCM more from CanBus.
* Describe byte order (BIG and LITTLE ENDIAN) better, and bit order. Byte-order, it is a property of the signal or the frame.

