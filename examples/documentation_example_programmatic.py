import can4python as can

frame_def = can.CanFrameDefinition(7, name='testmessage')
frame_def.producer_ids = ["1"]
signal_def = can.CanSignalDefinition("testsignal2", 0, 16)

frame_def.signaldefinitions.append(signal_def)
config = can.Configuration({7: frame_def}, ego_node_ids=["1"])

bus = can.CanBus(config, 'vcan0')
bus.send_signals({'testsignal2': 3}) # Signal value = 3 
