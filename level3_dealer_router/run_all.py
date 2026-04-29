import multiprocessing
import time

from router_server import main as router_main
from dealer_client import main as client_main

NUM_CLIENTS = 3

if __name__ == "__main__":
    server = multiprocessing.Process(target=router_main)
    server.start()
    time.sleep(1)

    clients = [multiprocessing.Process(target=client_main, args=(i,)) for i in range(NUM_CLIENTS)]
    for c in clients:
        c.start()
    
    for c in clients:
        c.join()
    
    server.terminate()
    server.join()
    print("All done!")