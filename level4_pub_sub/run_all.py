import multiprocessing
import time

from publisher import main as publisher_main
from subscriber import main as subscriber_main

if __name__ == "__main__":
    # First connect subs
    subs = [multiprocessing.Process(target=subscriber_main, args=(i,)) for i in range(3)]

    for sub in subs:
        sub.start()
    
    time.sleep(2)

    pub = multiprocessing.Process(target=publisher_main)
    pub.start()

    for s in subs:
        s.join()
    
    pub.terminate()
    pub.join()
    print(f"\n Done..")