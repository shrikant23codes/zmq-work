import zmq
import time
import random
import sys

TASKS_ADDR = "ipc:///tmp/tasks.ipc"
RESULTS_ADDR = "ipc:///tmp/results.ipc"

def main(worker_id: int):
    print(f"Starting worker {worker_id}...")
    context = zmq.Context()
    pull_socket = context.socket(zmq.PULL)
    pull_socket.connect(TASKS_ADDR)

    push_socket = context.socket(zmq.PUSH)
    push_socket.connect(RESULTS_ADDR)

    print(f"[WORKER-{worker_id}] Connected to tasks at {TASKS_ADDR} and results at {RESULTS_ADDR}")

    while True:
        task = pull_socket.recv_json()
        delay = random.uniform(0.5, 2.0)  # Simulate variable processing time
        time.sleep(delay)

        word_count = len(task["text"].split())
        push_socket.send_json({
            "task_id": task["task_id"],
            "worker_id": worker_id,
            "word_count": word_count,
            "ms": round(delay * 1000, 2)
        })

        print(f"[WORKER-{worker_id}] task {task['task_id']:02d} → {word_count} words ({round(delay*1000)}ms)")


if __name__ == "__main__":
    worker_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    main(worker_id)
