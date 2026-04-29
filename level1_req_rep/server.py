import zmq


def main():
    print("Starting server...")
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # Reply only socket
    socket.bind("tcp://127.0.0.1:5555")
    print(f"KV server listening on port 5555")

    # Need a while True loop to keep the server running and able to handle multiple requests

    store = {}
    while True:
        message = socket.recv_string()
        print(f"Received request <-: {message}")

        parts = message.split(" ", 2)
        command = parts[0].upper()

        if command == "SET" and len(parts) == 3:
            store[parts[1]] = parts[2]
            reply = "OK"
        elif command == "GET" and len(parts) == 2:
            reply = store.get(parts[1], "Key not found")
        elif command == "DEL" and len(parts) == 2:
            existed = store.pop(parts[1], None)
            reply = "OK" if existed is not None else "0"
        elif command == "KEYS":
            reply = " ".join(store.keys()) if store else "(empty)"
        else:
            reply = "Invalid command"
        
        print(f"Sending reply ->: {reply}")
        socket.send_string(reply)


if __name__ == "__main__":
    main()
