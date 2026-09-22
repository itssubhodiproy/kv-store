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
  ├─ replication (N=3, W=2, R=2)
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

The proxy maintains live node membership from etcd, routes keys using consistent hashing, replicates them across storage nodes, and coordinates read/write quorums over gRPC.

Each storage node runs an LSM-style engine:

```text
Write: WAL → MemTable → SSTable flush
Read:  MemTable → newest SSTable → Bloom filter → sparse index → disk
```

## Implemented

* HTTP GET / PUT / DELETE API
* gRPC proxy → storage communication
* consistent hashing with virtual nodes
* replication with read/write quorums (N=3, R=2, W=2)
* versioned values + last-write-wins read reconciliation
* etcd node discovery, leases + live membership watch
* persistent gRPC channels per storage node
* WAL + crash recovery
* AVL-tree MemTable + versioned tombstones
* immutable numbered SSTables
* Bloom filters + sparse indexes
* Dockerized multi-node local cluster

## Run

```bash
docker compose up --build
```

Proxy runs on `localhost:8000`.

## Status

Working distributed routing, durable local storage, quorum replication, and version-based read reconciliation.

Built as a learning project; not intended to be a production database.