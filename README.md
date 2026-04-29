ZeroMQ Plan (Python)

  Level 1 — REQ/REP: Synchronous Echo Server

  The simplest pattern. One client asks, one server replies. Blocking on both sides.

  Build: A simple key-value store server where the client sends SET key val / GET key as strings, server responds.

  Concepts: zmq.PUSH, bind() vs connect(), send_string() / recv_string(), what happens when server is slow.

  DONE 

  ---
  Level 2 — PUSH/PULL: Task Queue (Pipeline)

  Unidirectional. No reply needed. Multiple workers can pull from one queue.

  Build: A "tokenizer farm" — one producer pushes text strings, 3 worker processes pull and return word counts, a sink collects results.

  Concepts: fan-out, ipc:// transport (local IPC, not TCP), process spawning with multiprocessing.

  

  ---
  Level 3 — DEALER/ROUTER: Async Request-Reply

  This is where vLLM actually lives. REQ/REP is blocking; DEALER/ROUTER breaks that.

  Build: An async echo server where clients send requests with correlation IDs, the server handles them out of order, clients match responses by ID.

  Concepts: identity frames, multipart messages (send_multipart), zmq.NOBLOCK, zmq.POLLIN with Poller.

  ---
  Level 4 — PUB/SUB: Status Broadcasting

  Jupyter uses this — the kernel broadcasts execute_result, stream, status messages to notebooks.

  Build: An "engine status broadcaster" — a server publishes {request_id, status, partial_result} frames; multiple subscribers filter by prefix.

  Concepts: topic filtering, slow subscriber problem, zmq.CONFLATE.

  ---
  Level 5 — Multi-Process IPC with Asyncio

  Bridge zmq into async Python. vLLM's AsyncLLMEngine does exactly this.

  Build: A compute engine that runs in a separate process. Main process sends requests over zmq, engine process handles them async, streams back results.
  Use asyncio + zmq.asyncio.

  Concepts: zmq.asyncio.Context, running the zmq loop alongside asyncio.sleep, serialization with msgpack or pickle.

  ---
  Level 6 — Mini vLLM Engine Core

  Replicate the actual vLLM pattern: HTTP layer → zmq frontend → engine process → zmq backend → workers.

  Build:
  - api_server.py — FastAPI server, receives HTTP requests
  - engine_core.py — spawned subprocess, owns a ROUTER socket, processes requests with simulated latency, streams token-by-token responses back
  - worker.py — PULL worker that engine distributes to

  Concepts: process isolation, ipc://tmp/engine.sock-style sockets, why vLLM chose this over threading (GIL, CUDA context isolation), graceful shutdown
  signals over zmq.

  ---
  Suggested Stack Per Project

  ┌───────┬───────────┬───────────────────────────┬─────────────────┐
  │ Level │ Transport │          Pattern          │  Serialization  │
  ├───────┼───────────┼───────────────────────────┼─────────────────┤
  │ 1     │ tcp://    │ REQ/REP                   │ plain string    │
  ├───────┼───────────┼───────────────────────────┼─────────────────┤
  │ 2     │ ipc://    │ PUSH/PULL                 │ string          │
  ├───────┼───────────┼───────────────────────────┼─────────────────┤
  │ 3     │ ipc://    │ DEALER/ROUTER             │ multipart bytes │
  ├───────┼───────────┼───────────────────────────┼─────────────────┤
  │ 4     │ tcp://    │ PUB/SUB                   │ JSON            │
  ├───────┼───────────┼───────────────────────────┼─────────────────┤
  │ 5     │ ipc://    │ DEALER/ROUTER             │ msgpack         │
  ├───────┼───────────┼───────────────────────────┼─────────────────┤
  │ 6     │ ipc://    │ ROUTER/DEALER + PUSH/PULL │ msgpack         │
  └───────┴───────────┴───────────────────────────┴─────────────────┘