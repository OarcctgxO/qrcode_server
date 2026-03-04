port = 8888
server_addr = ('0.0.0.0', port)
udp_wait_time = 2

broadcast_addr = ('255.255.255.255', port)
udp_request = b"Who's QRcode server?"
udp_response = b"I am the QRcode server."
udp_kill = b"QRcode servers must shutdown."

logo_path = 'logo.png'
correction_level = {
    'minimum': 1,
    'medium': 0,
    'high': 3,
    'maximum': 2
}
workers = 50