import zmq

"""
Some learnings:
- REQ socket expects a strict send-receive pattern. After sending a request, it must wait for a reply before sending another request.
- If a server is not running or not reachable, the client will block indefinitely on recv_string() waiting for a reply that will never come.
-  We can set a timeout on socket to avoid above case.

"""

def main():
    print("Starting client...")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # Request only socket
    socket.connect("tcp://127.0.0.1:5555")
    print("Connect to server on port 5555 -> Commands to use: GET key | SET key value | DEL key | KEYS")

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            break

        socket.send_string(line)
        # Below send would not work,
        # ERROR: zmq.error.ZMQError: Operation cannot be accomplished in current state
        # Because REQ socket expects a strict send-receive pattern. After sending a request, it must wait for a reply before sending another request.
        # socket.send_string(line)
        reply = socket.recv_string()

        print(reply)
    socket.close()
    context.term()


if __name__ == "__main__":
    main()