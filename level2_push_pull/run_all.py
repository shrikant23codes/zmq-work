import multiprocessing
import os
import time

from sink import main as sink_main
from producer import main as producer_main
from worker import main as worker_main

NUM_WORKERS = 3

"""

Proper sync and order of all processes in crucial.
- Sink must start first to bind to the results socket before any worker tries to connect.
- Workers can start next to connect to the sink's results socket and wait for tasks.
- Producer starts last to bind to the tasks socket and dispatch tasks to workers.

w.terminate() is async we need w.join() to avoid stale reuse

"""

if __name__ == "__main__":
    # cleanup must be inside the guard — on macOS (spawn), module-level code
    # re-runs in every child process, which would delete socket files that
    # the sink already bound to
    for path in ["/tmp/tasks.ipc", "/tmp/results.ipc"]:
        if os.path.exists(path):
            os.remove(path)

    # Order matters here - start sink, then workers, then producer

    sink_process = multiprocessing.Process(target=sink_main)
    sink_process.start()
    time.sleep(5)  # Allow sink to start and bind before workers connect

    workers = [multiprocessing.Process(target=worker_main, args=(wid,)) for wid in range(NUM_WORKERS)]

    for w in workers:
        w.start()
    
    time.sleep(0.5)

    producer = multiprocessing.Process(target=producer_main)
    producer.start()

    sink_process.join()
    producer.join()
    for w in workers:
        w.terminate() # To stop infinite loop in workers after producer is done
        w.join()