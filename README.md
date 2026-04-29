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

  