[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Etw90P0Z)
# DIPPID and Pyglet

## Assignment 01: DIPPID Sender Simulation

This assignment demonstrates simulating DIPPID input devices using UDP communication.

### Requirements
- Python 3.x
- DIPPID library (included in workspace)

### Running the DIPPID Sender

1. Navigate to the `dippid_sender` directory:
   ```bash
   cd dippid_sender
   ```

2. Run the sender script:
   ```bash
   python DIPPID_sender.py
   ```
   Or with custom options:
   ```bash
   python DIPPID_sender.py --host 127.0.0.1 --port 5700 --interval 0.05
   ```

   The sender will simulate accelerometer (x/y/z values) and button_1, sending JSON packets via UDP.

3. To stop: Press `Ctrl+C`.

### Testing with Receiver

To verify the sender, run a receiver in another terminal:

1. In `dippid_sender` directory, run:
   ```bash
   python demo_heartbeat.py
   ```
   (Modified to handle accelerometer and button_1 data)

2. The receiver will print received data, confirming UDP packets arrive correctly.

### Output Example
Sender output:
```
Starting DIPPID sender to 127.0.0.1:5700
Sent 20 packets. Last: {"accelerometer": {"x": 0.8476, "y": -0.1234, "z": 1.0567}, "button_1": 0}
```

Receiver output:
```
Received: {'accelerometer': {'x': 0.8476, 'y': -0.1234, 'z': 1.0567}, 'button_1': 0}
```




## 2D Game: SNAKE
To control the Snake game using a smartphone, both the computer and the phone must be connected to the same WiFi network.

### Get the computer IP address

Open the terminal and run: 
```bash
ipconfig getifaddr en0
```

Output Example:
```
192.168.178.25
```
This IP address must be used as the host in the DIPPID app.

### Configuring the DIPPID App
Set the following values in the DIPPID app:
```
Host: <computer IP address>
Port: 5700
```
### Running the Game
Start the Snake game:
```bash
python snake.py
```
The game listens for incoming sensor data on port 5700 using a UDP receiver.
Movement direction is controlled by the accelerometer values received from the smartphone.
