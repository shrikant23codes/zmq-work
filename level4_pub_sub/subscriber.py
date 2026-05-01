import zmq
import time
import sys

ADDR = "tcp://127.0.0.1:5555"

SUBSCRIPTIONS = {
    0: [b"TOKEN-req-001", b"STATUS"],
    1: [b"TOKEN-req-002"],
    2: [b""]
}


def main(sub_id: int):
    print("Starting subscriber..")
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(ADDR)

    print(f"Subscriber {sub_id} connected to {ADDR}")

    # Get topics
    topics = SUBSCRIPTIONS.get(sub_id, [b""])

    for topic in topics:
        socket.setsockopt(zmq.SUBSCRIBE, topic)
    
    labels = [t.decode() or "all" for t in topics]

    print(f"Subscriber {sub_id} subscribed to topics: {labels}")

    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    while True:
        socks = dict(poller.poll(5000))
        if not socks:
            print(f"[SUB-{sub_id}] No messages received in the last 3 seconds. Stopping..")
            break
        topic, payload = socket.recv_multipart()
        print(f"[sub-{sub_id}]  [{topic.decode()}]  {payload.decode()}")
    
    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()


if __name__ == "__main__":
    sub_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    main(sub_id)
