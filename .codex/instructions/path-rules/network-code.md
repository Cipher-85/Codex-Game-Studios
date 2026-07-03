# Network Code Rules

---
paths:
  - "src/networking/**"
---

- The server is authoritative for all gameplay-critical state; never trust the
  client.
- All network messages must be versioned for forward and backward compatibility.
- Client predicts locally and reconciles with the server; implement rollback for
  mispredictions.
- Handle disconnection, reconnection, and host migration gracefully.
- Rate-limit all network logging to prevent log flooding.
- All networked values must specify replication strategy: reliable or
  unreliable, frequency, and interpolation.
- Define and track bandwidth usage per message type.
- Validate all incoming packet sizes and field ranges.
