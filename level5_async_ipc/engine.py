import asyncio
import zmq
import zmq.asyncio
import os
import msgpack
import random

ADDR = "ipc:///tmp/zmq-engine.ipc"

async def generate_tokens(prompt):
    for word in prompt.split():
        await asyncio.sleep(random.uniform(0.05, 0.15))
        yield word


async def handle_request(socket, identity, request):
    print(f"[ENGINE] {request['request_id']} - {request['prompt']}")

    async for token in generate_tokens(request['prompt']):
        await socket.send_multipart([identity, msgpack.dumps({"request_id": request['request_id'], "token": token, "done": False}),])
    
    await socket.send_multipart([identity, msgpack.dumps({"request_id": request['request_id'],  "token": "", "done": True}),])
    print(f"  [engine] {request['request_id']} done")


async def main():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind(ADDR)
    print(f"Engine is listening on {ADDR}")

    # Receive requests in while True
    while True:
        identity, payload = await socket.recv_multipart()
        request = msgpack.loads(payload, raw=False)
        # No need to gather the tasks, just create them and let them run in the background
        asyncio.create_task(
            handle_request(socket, identity, request)
        )

if __name__ == "__main__":
    if os.path.exists("/tmp/zmq-engine.ipc"):
        os.remove("/tmp/zmq-engine.ipc")
    asyncio.run(main())