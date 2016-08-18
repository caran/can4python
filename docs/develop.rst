=====================
Developer information
=====================


KCD file validation
-------------------
The KCD file format is described here: https://github.com/julietkilo/kcd

There is an example file as well as a XML schema definition file (.XSD format).

Use some online XML schema validator service to make sure the imported and exported KCD files to/from can4python are valid.


Header for BCM communication
----------------------------
The BCM header has this format:

* opcode, u32 (4 bytes)
* flags, u32 (4 bytes)
* ival1_count, u32 (4 bytes)
* (possible paddding, 4 bytes)
* ival1_seconds, long (platform dependent, 4 or 8 bytes)
* ival1_useconds, long (platform dependent, 4 or 8 bytes)
* ival2_seconds, long (platform dependent, 4 or 8 bytes)
* ival2_useconds, long (platform dependent, 4 or 8 bytes)
* frame_id_std_ext, 32 bits (4 bytes)
* number_of_bcm_frames, u32 (4 bytes)
* (possible paddding, 4 bytes)

Use the 'native' byte alignment character to have automatic alignment between the different struct members.
It is necessary to align the header end to 8 bytes, as there are CAN frames afterwards. Use zero occurances of an 8-byte struct member.



TODO
----
* Handle Labels (Enums, name constants) in KCD files. For example: PowerMode='EngineRunning'
* More usage examples, also with BCM.
* Implement a get_configuration() function.
* Implement myconfiguration.get_all_signalnames()
* Abstract BCM more from CanBus.
* Describe byte order (BIG and LITTLE ENDIAN) better, and bit order. Byte-order, it is a property of the signal or the frame.
