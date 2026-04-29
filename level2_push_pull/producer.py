import zmq
import time

"""
Some learnings:
- using ipc:// for local server. in vLLM API server and engine core use ipc as they are co-location on same machine.
- PUSH type requires a PULL socket otherwise it will be stuck on send_json()
- No feedback which worker got the task and when it is done.
"""

TASKS_ADDR = "ipc:///tmp/tasks.ipc"

TEXTS = [
      "the quick brown fox jumps over the lazy dog",
      "zmq push pull distributes work across many workers",
      "python multiprocessing spawns real OS processes",
      "ipc transport uses unix domain sockets not tcp",
      "the sink collects results from all workers",
      "each worker pulls tasks independently",
      "fair queuing ensures round robin distribution",
      "high water mark controls backpressure in zmq",
      "dealer router pattern enables async request reply",
      "vllm uses zmq for engine to api server communication",
]

def main():
    print(f"Starting producer..")
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.bind(TASKS_ADDR)
    print(f"Producer bound to {TASKS_ADDR}..")

    time.sleep(1)  # Allow workers to connect before sending tasks

    for task_id, text in enumerate(TEXTS):
        task = {"task_id": task_id, "text": text}
        # PUSH type requires a PULL socket otherwise it will be stuck on send_json()
        socket.send_json(task)
        print(f"Dispatched task -> {task_id}")

    print("Producer done dispatching tasks.")
    socket.setsockopt(zmq.LINGER, 1000)  # Wait up to 1 second for pending messages to be sent before closing
    socket.close()
    context.term()


if __name__ == "__main__":
    main()
