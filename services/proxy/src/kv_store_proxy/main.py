import asyncio
import os

import uvicorn

from .api import app
from .hash_ring import HashRing
from .registry import NodeRegistry
from .storage_client import StorageClient


async def watch_nodes(registry, ring, revision):
    async for event_type, node_id in registry.watch_nodes(revision + 1):
        if event_type == "PUT":
            ring.add_node(node_id)
        else:
            ring.remove_node(node_id)

        print(f"{event_type} {node_id}")


async def serve():
    registry = NodeRegistry(os.getenv("ETCD_ENDPOINT", "http://localhost:2379"))
    ring = HashRing()
    storage_client = StorageClient()

    app.state.registry = registry
    app.state.ring = ring
    app.state.storage_client = storage_client

    try:
        nodes, revision = await registry.load_nodes()

        for node_id in nodes:
            ring.add_node(node_id)

        watch_task = asyncio.create_task(watch_nodes(registry, ring, revision))

        server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=8000))

        await server.serve()

        watch_task.cancel()

    finally:
        await storage_client.close()
        await registry.close()


def main():
    asyncio.run(serve())


if __name__ == "__main__":
    main()
