from DIPPID import SensorUDP

PORT = 5700
sensor = SensorUDP(PORT)

def handle_data(data):
    print("Received:", data)

sensor.register_callback('accelerometer', handle_data)
sensor.register_callback('button_1', handle_data)