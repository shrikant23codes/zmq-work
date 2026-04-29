import zmq
from collections import defaultdict

RESULTS_ADDR = "ipc:///tmp/results.ipc"
TOTAL_TASKS = 10


def main():
    print("Starting sink..")
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(RESULTS_ADDR)

    print(f"[SINK] Bound to {RESULTS_ADDR}.. and expecting {TOTAL_TASKS} results..")

    tally = defaultdict(list)

    for _ in range(TOTAL_TASKS):
        print(f"[SINK] Waiting for results..")
        task_result = socket.recv_json()
        tally[task_result["worker_id"]].append(task_result)
        print(f"[SINK]  ← task {task_result['task_id']:02d} | worker-{task_result['worker_id']} | {task_result['word_count']} words | {task_result['ms']}ms")

    print("\n[SINK] Summary ----")
    for wid in sorted(tally):
        tasks_done = len(tally[wid])
        avg_ms = round(sum(r["ms"] for r in tally[wid]) / tasks_done, 2)
        print(f"[SINK]  → worker-{wid} | {tasks_done} tasks | avg {avg_ms}ms")
    
    socket.close()
    context.term()


if __name__ == "__main__":
    main()
