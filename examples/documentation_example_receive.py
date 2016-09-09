import can4python as can

bus = can.CanBus.from_kcd_file('documentation_example.kcd', 'vcan0', ego_node_ids=["2"])
received_signalvalues = bus.recv_next_signals()
print(received_signalvalues)
