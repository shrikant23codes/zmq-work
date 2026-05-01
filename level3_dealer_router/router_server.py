import zmq
from queue import Queue
import json
import threading
import random
import time

ADDR = "tcp://127.0.0.1:5555"

"""
Router server starts a poller to receive requests from clients. Then for each request it does async processing.
Once processing it done, it reads from queue and does send to clients
"""

def process(identity, request, reply_queue):
    delay = random.uniform(0.1, 1.0)
    time.sleep(delay)
    reply_queue.put((identity, json.dumps({
        "request_id": request["request_id"],
        "result": request["value"] ** 2,
        "delay_ms": round(delay * 1000, 2)
    }).encode()))


def main():
    print("Starting router server...")
    context = zmq.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind(ADDR)
    print(f"Router server bound to {ADDR}..")

    reply_queue = Queue()

    # Create poller
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    while True:
        socks = dict(poller.poll(timeout=10))  # 10ms poll,

        # Any data to read on our socket?
        if socket in socks:
            frames = socket.recv_multipart()
            identity, payload = frames[0], frames[1]
            request = json.loads(payload.decode())
            print(f"[ROUTER] Received request from {identity}: {request}")

            threading.Thread(
                target=process,
                args=(identity, request, reply_queue),
                daemon=True
            ).start()
        
        # Check if any replies are ready to be sent back
        while not reply_queue.empty():
            identity, reply = reply_queue.get_nowait()
            socket.send_multipart([identity, reply])
            r = json.loads(reply)
            print(f"  → [{identity}] req {r['request_id']}: {r['result']} ({r['delay_ms']}ms)") 


if __name__ == "__main__":
    main()
