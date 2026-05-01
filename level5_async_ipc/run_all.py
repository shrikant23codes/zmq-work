import multiprocessing
import asyncio
import os
import time

from engine import main as engine_main
from client import main as client_main

def run_engine():
    if os.path.exists("/tmp/zmq-engine.ipc"):
        os.remove("/tmp/zmq-engine.ipc")
    asyncio.run(engine_main())

def run_client(client_id):
    asyncio.run(client_main(client_id))


if __name__ == "__main__":
    print(f"Starting engine and client processes...")

    engine = multiprocessing.Process(target=run_engine)
    engine.start()
    time.sleep(1)

    clients = [multiprocessing.Process(target=run_client, args=(i,)) for i in range(2)]

    for c in clients:
        c.start()
    
    for c in clients:
        c.join()
    
    engine.terminate()
    engine.join()

    print("All processes finished.")