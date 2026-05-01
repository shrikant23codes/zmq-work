import zmq
import time
import threading
import random

ADDR = "tcp://127.0.0.1:5555"

REQUESTS = {
      "req-001": "The quick brown fox jumps over the lazy dog".split(),
      "req-002": "ZeroMQ is a lightweight messaging library".split(),
      "req-003": "Python makes distributed systems easy to build".split(),
}


def stream_tokens(socket, lock, req_id, tokens):
    for token in tokens:
        time.sleep(random.uniform(0.5, 1.5))
        with lock:
            socket.send_multipart([f"TOKEN-{req_id}".encode(), token.encode()])
    with lock:
        socket.send_multipart([b"DONE ", req_id.encode()])
        print(f"[PUB] Finished request {req_id}")


def main():
    print("Starting publisher..")
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(ADDR)
    print(f"Publisher bound to {ADDR}")

    time.sleep(1)  # Allow subs to connect

    socket.send_multipart([b"STATUS", b"Starting publish.."])
    lock = threading.Lock()

    threads = [
        threading.Thread(target=stream_tokens, args=(socket, lock, req_id, tokens), daemon=True)
        for req_id, tokens in REQUESTS.items()
    ]

    for thread in threads:
        thread.start()
    
    socket.send_multipart([b"STATUS", b"processing"])
    
    for thread in threads:
        thread.join()
    
    socket.send_multipart([b"STATUS", b"idle"])
    print(f"[PUB] All requests processed. Publisher is idle.")
    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()

if __name__ == "__main__":
    main()