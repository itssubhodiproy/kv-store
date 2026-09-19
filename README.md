# KV Store

Distributed key-value store built from scratch to learn storage engines and distributed systems internals.

## Architecture

```text
Client
  │ HTTP
  ▼
Proxy
  ├─ etcd service discovery + watch
  ├─ consistent hashing + virtual nodes
  └─ persistent gRPC channels
        │
        ▼
   Storage Nodes
        │
        ├─ WAL
        ├─ AVL MemTable
        └─ SSTables
            ├─ Bloom filters
            └─ sparse indexes
```

The proxy maintains live node membership from etcd, routes keys using consistent hashing, then forwards GET/PUT/DELETE to the owning storage node over gRPC.

Each storage node runs an LSM-style engine:

```text
Write: WAL → MemTable → SSTable flush
Read:  MemTable → newest SSTable → Bloom filter → sparse index → disk
```

## Implemented

* HTTP GET / PUT / DELETE API
* gRPC proxy → storage communication
* consistent hashing with virtual nodes
* etcd node discovery, leases + live membership watch
* persistent gRPC channels per storage node
* WAL + crash recovery
* AVL-tree MemTable + tombstones
* immutable numbered SSTables
* Bloom filters + sparse indexes
* Dockerized multi-node local cluster

## Run

```bash
docker compose up --build
```

Proxy runs on `localhost:8000`.

## Status

Working distributed routing + single-node durable storage.

Next: replication, consistency/quorums, failure handling, and rebalancing.
