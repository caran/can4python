import os
import can4python
THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
kcdfile_full_path = os.path.join(THIS_DIRECTORY, 'documentation_example.kcd')

bus = can4python.CanBus.from_kcd_file(kcdfile_full_path, 'vcan0', ego_node_ids=["1"])
print(bus.get_descriptive_ascii_art())
