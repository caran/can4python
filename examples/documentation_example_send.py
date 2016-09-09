import can4python as can

bus = can.CanBus.from_kcd_file('documentation_example.kcd', 'vcan0', ego_node_ids=["1"])
bus.send_signals({'testsignal2': 3}) # Signal value = 3 
