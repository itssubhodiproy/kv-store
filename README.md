# KV Store

A distributed key-value store built from scratch for learning how storage engines and distributed databases work internally.

Currently implements a single-node LSM-style storage engine with:

* AVL tree-based MemTable
* Write-ahead log (WAL) with recovery
* Immutable SSTables
* Bloom filters
* Sparse indexes
* Disk-based reads

## Run

```bash
uv run kv-store
```

## Status

Work in progress. Currently focused on the single-node storage engine. Distributed routing, replication, and coordination will be added later.
