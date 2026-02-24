port = 8888
server_addr = ('0.0.0.0', port)
udp_wait_time = 3

broadcast_addr = ('255.255.255.255', port)
udp_request = b"Who's QRcode server?"
udp_response = b"I am the QRcode server."

logo_path = 'logo.png'
correction_level = {
    'minimum': 1,
    'medium': 0,
    'high': 3,
    'maximum': 2
}
thread_pool_limit = 50