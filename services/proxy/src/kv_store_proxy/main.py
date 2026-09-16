import asyncio
import os

from .hash_ring import HashRing
from .registry import NodeRegistry


async def serve():
    etcd_endpoint = os.getenv("ETCD_ENDPOINT", "http://localhost:2379")
    registry = NodeRegistry(etcd_endpoint)
    ring = HashRing()

    try:
        nodes, revision = await registry.load_nodes()

        for node_id in nodes:
            ring.add_node(node_id)

        print(f"Discovered nodes: {nodes}")

        async for event_type, node_id in registry.watch_nodes(revision + 1):
            if event_type == "PUT":
                ring.add_node(node_id)
            else:
                ring.remove_node(node_id)

            print(f"{event_type} {node_id}")
    
    finally:
        await registry.close()


def main():
    asyncio.run(serve())


if __name__ == "__main__":
    main()
