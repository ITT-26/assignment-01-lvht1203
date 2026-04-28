import argparse
import json
import math
import random
import signal
import socket
import sys
import time


class SimulatedDIPPIDSender:
    """Simulate a DIPPID input device and send UDP packets to a DIPPID receiver."""

    def __init__(self, host='127.0.0.1', port=5700, interval=0.05, seed=None):
        """Initialize the sender with UDP socket and simulation parameters.
        
        Args:
            host (str): Destination IP address (default: localhost).
            port (int): Destination UDP port (default: 5700).
            interval (float): Time between packets in seconds (default: 0.05).
            seed (int): Random seed for reproducible button behavior.
        """
        self.host = host
        self.port = port
        self.interval = interval
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.start_time = time.time()
        self.running = False
        self.button_state = 0  # 0 = released, 1 = pressed
        self.random = random.Random(seed)
        self.next_button_toggle = self.start_time + self._random_button_interval()
        self.button_press_duration = 0.0
        self.button_release_duration = 0.0

    def _random_button_interval(self):
        """Generate a random interval for button press/release (1-3.5 seconds)."""
        return self.random.uniform(1.0, 3.5)

    def _random_button_duration(self):
        """Generate a random duration for button press (0.1-0.5 seconds)."""
        return self.random.uniform(0.1, 0.5)

    def _simulate_accelerometer(self, elapsed):
        """Simulate accelerometer values using sine waves with different frequencies and phases.
        
        Args:
            elapsed (float): Time elapsed since start.
        
        Returns:
            dict: {'x': float, 'y': float, 'z': float} with values between -1.2 and 1.2.
        """
        # Different frequencies and phases to simulate realistic movement
        x = math.sin(elapsed * 2.0 * math.pi * 0.6) * 1.2  # Frequency 0.6 Hz
        y = math.sin(elapsed * 2.0 * math.pi * 0.9 + math.pi / 4) * 1.0  # 0.9 Hz, phase shift
        z = math.sin(elapsed * 2.0 * math.pi * 0.4 + math.pi / 2) * 1.1  # 0.4 Hz, phase shift
        return {'x': round(x, 4), 'y': round(y, 4), 'z': round(z, 4)}

    def _simulate_button(self, now):
        """Simulate button press/release with random timing.
        
        Args:
            now (float): Current time.
        
        Returns:
            int: 0 (released) or 1 (pressed).
        """
        if now >= self.next_button_toggle:
            if self.button_state == 0:
                # Start pressing the button
                self.button_state = 1
                self.button_press_duration = self._random_button_duration()
                self.next_button_toggle = now + self.button_press_duration
            else:
                # Release the button
                self.button_state = 0
                self.button_release_duration = self._random_button_interval()
                self.next_button_toggle = now + self.button_release_duration
        return self.button_state

    def _build_packet(self, now):
        """Build a JSON packet with current sensor data.
        
        Args:
            now (float): Current time.
        
        Returns:
            str: JSON string with accelerometer and button_1 data.
        """
        elapsed = now - self.start_time
        packet = {
            'accelerometer': self._simulate_accelerometer(elapsed),
            'button_1': self._simulate_button(now),
        }
        return json.dumps(packet)

    def run(self):
        """Run the sender loop: simulate data and send UDP packets until stopped."""
        self.running = True
        print(f'Starting DIPPID sender to {self.host}:{self.port}')
        packet_count = 0
        try:
            while self.running:
                now = time.time()
                packet = self._build_packet(now)
                try:
                    self.socket.sendto(packet.encode('utf-8'), (self.host, self.port))
                    packet_count += 1
                    if packet_count % 20 == 0:  # Print every 20 packets to avoid spamming
                        print(f'Sent {packet_count} packets. Last: {packet}')
                except OSError as error:
                    print(f'Failed to send packet: {error}', file=sys.stderr)
                    break
                time.sleep(self.interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def run_manual(self):
        """Run a manual sender that sends tilt commands from typed input."""
        self.running = True
        print(f'Starting manual DIPPID sender to {self.host}:{self.port}')
        print('Type left/right/up/down/stop/quit and press Enter.')
        try:
            while self.running:
                try:
                    command = input('Command: ').strip().lower()
                except EOFError:
                    break

                if command in ('quit', 'exit'):
                    break

                if command == 'stop':
                    accel = {'x': 0.0, 'y': 0.0, 'z': 0.0}
                elif command == 'left':
                    accel = {'x': -1.0, 'y': 0.0, 'z': 0.0}
                elif command == 'right':
                    accel = {'x': 1.0, 'y': 0.0, 'z': 0.0}
                elif command == 'up':
                    accel = {'x': 0.0, 'y': 1.0, 'z': 0.0}
                elif command == 'down':
                    accel = {'x': 0.0, 'y': -1.0, 'z': 0.0}
                elif command == 'button':
                    packet = json.dumps({'accelerometer': {'x': 0.0, 'y': 0.0, 'z': 0.0}, 'button_1': 1})
                    self.socket.sendto(packet.encode('utf-8'), (self.host, self.port))
                    print(f'Sent button packet: {packet}')
                    continue
                else:
                    print('Unknown command, use left/right/up/down/stop/button/quit')
                    continue

                packet = json.dumps({'accelerometer': accel, 'button_1': 0})
                self.socket.sendto(packet.encode('utf-8'), (self.host, self.port))
                print(f'Sent packet: {packet}')
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        """Stop the sender and close the socket."""
        if self.running:
            print('Stopping DIPPID sender.')
        self.running = False
        try:
            self.socket.close()
        except OSError:
            pass


def parse_args():
    """Parse command-line arguments for the sender."""
    parser = argparse.ArgumentParser(description='Simulate a DIPPID input device sent over UDP to localhost.')
    parser.add_argument('--host', default='127.0.0.1', help='Destination host for UDP packets (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5700, help='Destination UDP port (default: 5700)')
    parser.add_argument('--interval', type=float, default=0.05, help='Packet send interval in seconds (default: 0.05)')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for button behavior')
    parser.add_argument('--manual', action='store_true', help='Use manual typed commands instead of automatic tilt simulation')
    return parser.parse_args()


def main():
    """Main entry point: parse args, create sender, and run until interrupted."""
    args = parse_args()
    sender = SimulatedDIPPIDSender(host=args.host, port=args.port, interval=args.interval, seed=args.seed)

    def handle_stop_signal(signum, frame):
        sender.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_stop_signal)
    signal.signal(signal.SIGTERM, handle_stop_signal)

    if args.manual:
        sender.run_manual()
    else:
        sender.run()


if __name__ == '__main__':
    main()
