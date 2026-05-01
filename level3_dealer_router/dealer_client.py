import zmq
import time
import random
import json
import sys

ADDR = "tcp://127.0.0.1:5555"
NUMBER_OF_REQUESTS = 5

"""
Client first sends all requests to router server.
Then starts a poller to wait for replies.
"""

def main(client_id: int):
    print(f"Starting dealer client...")
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.connect(ADDR)
    print(f"Dealer client connected to {ADDR}..")

    send_times = {}

    for i in range(NUMBER_OF_REQUESTS):
        request_id = f"c{client_id}-req{i}"
        value = random.randint(1, 10)
        socket.send_multipart([json.dumps({"request_id": request_id, "value": value}).encode()])
        send_times[request_id] = time.time()
        print(f"[DEALER] -- {client_id} sent request {request_id} with value {value}")
    
    # Setup poller to wait for replies
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    received_replies = 0

    while received_replies < NUMBER_OF_REQUESTS:
        socks = dict(poller.poll(timeout=5000))  # 5 sec
        if not socks:
            print(f"[DEALER] -- {client_id} timed out waiting for replies")
            break
        frames = socket.recv_multipart()
        reply = json.loads(frames[0].decode())
        round_trip_time = round((time.time() - send_times[reply["request_id"]]) * 1000, 2)
        print(f"[client-{client_id}] ← recv {reply['request_id']}: {reply['result']} (RTT {round_trip_time}ms)")
        received_replies += 1
    
    print(f"[DEALER] - {client_id} DONE")
    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()



if __name__ == "__main__":
    client_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    main(client_id)
