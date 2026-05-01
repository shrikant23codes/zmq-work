import zmq
import zmq.asyncio
import asyncio
import msgpack
import sys

ADDR = "ipc:///tmp/zmq-engine.ipc"

async def recv_loop(socket, queues):
    print(f"[CLIENT] Starting recv loop...")
    while True:
        frames = await socket.recv_multipart()
        response = msgpack.loads(frames[0], raw=False)
        req_id = response['request_id']
        if req_id in queues:
            await queues[req_id].put(response)

# Run as independent task for each request.
async def stream_request(socket, queues, request_id, prompt):
    print(f"[CLIENT] Sending request {request_id}: {prompt}")
    # For each request, we create a new queue to receive the tokens from the engine
    queue: asyncio.Queue = asyncio.Queue()
    queues[request_id] = queue
    
    await socket.send_multipart([
        msgpack.dumps({"request_id": request_id, "prompt": prompt})
    ])

    tokens = []
    while True:
        response = await queue.get()
        if response['done']:
            break
        tokens.append(response['token'])
        print(f"[CLIENT][{request_id}] ← {response['token']}")
    
    print(f"[CLIENT] [{request_id}] done: {' '.join(tokens)}")
    del queues[request_id]



async def main(client_id: int):
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, f"client-{client_id}".encode())
    socket.connect(ADDR)
    print(f"Client {client_id} connected to {ADDR}")

    # Client does 2 things:
    # 1. Create a loop to receive responses from the engine

    queues: dict = {}
    recv_task = asyncio.create_task(recv_loop(socket, queues))

    await asyncio.gather(
        stream_request(socket, queues, f"c-{client_id}-A", "hello world from asyncio"),
        stream_request(socket, queues, f"c-{client_id}-B", "zmq and python work beautifully together"),
    )

    recv_task.cancel()

    try:
        await recv_task
    except asyncio.CancelledError:
        pass

    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    context.term()
    print(f"[CLIENT] -- {client_id} DONE")



if __name__ == "__main__":
    client_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    asyncio.run(main(client_id))