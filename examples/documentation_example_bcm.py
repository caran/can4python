import time
import can4python as can

frame_def = can.CanFrameDefinition(7, name='testmessage')
frame_def.producer_ids = ["1"]
frame_def.cycletime = 250 # milliseconds
signal_def = can.CanSignalDefinition("testsignal2", 0, 16)

frame_def.signaldefinitions.append(signal_def)
config = can.Configuration({7: frame_def}, ego_node_ids=["1"])

bus = can.CanBus(config, 'vcan0', use_bcm=True)
bus.send_signals({'testsignal2': 5}) # Signal value = 5. Start periodic transmission.
time.sleep(10)
