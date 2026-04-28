# import socket
# import json

# def test_udp_receiver():
#     """Test script to receive UDP packets from DIPPID app and print them."""
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.bind(('0.0.0.0', 5700))
#     print("Listening for UDP packets on port 5700...")
#     print("Send data from your DIPPID app to this machine's IP address.")
#     print("Press Ctrl+C to stop.")

#     try:
#         while True:
#             data, addr = sock.recvfrom(1024)
#             try:
#                 decoded = data.decode('utf-8')
#                 print(f"Received from {addr}: {decoded}")
#                 # Try to parse as JSON
#                 try:
#                     parsed = json.loads(decoded)
#                     print(f"Parsed JSON: {parsed}")
#                 except json.JSONDecodeError:
#                     print("Not valid JSON")
#             except UnicodeDecodeError:
#                 print(f"Received binary data from {addr}: {data}")
#     except KeyboardInterrupt:
#         print("Stopping...")
#     finally:
#         sock.close()

# if __name__ == "__main__":
#     test_udp_receiver()