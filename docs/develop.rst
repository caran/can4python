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
* Abstract BCM more from CanBus.


Release procedure
---------------------
Development is done in the 'dev' git branch.

To do a release:

* Change version number in the version.py file
* Update HISTORY.rst
* Run tests
* Verify that documentation builds for HTML and PDF works

Commit to dev, and push to master::

    git add HISTORY.rst 
    git add can4python/version.py 
    git commit -m "Version 0.2.0"
    git pull origin dev
    git push origin dev
    git checkout master
    git pull origin master
    git checkout dev
    git merge master
    git checkout master
    git merge dev
    git push origin master

Make a tag::

    git tag -a 0.2.0 -m "Version 0.2.0"
    git push origin --tags

Upload to PyPI::

    python3 setup.py register
    python3 setup.py sdist bdist_wheel upload

Update Readthedocs.io by clicking the "Build" button on the "Project Home" page.
You need to build within a virtualenv on Readthedocs to have API documnentation working (adjust the project settings).
Restrict Readthedocs.io to publish the "latest" branch of the documentation.
