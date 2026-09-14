import asyncio
import os

from .registry import NodeRegistry


async def serve():
    etcd_endpoint = os.getenv("ETCD_ENDPOINT", "http://localhost:2379")
    registry = NodeRegistry(etcd_endpoint)

    try:
        nodes, revision = await registry.load_nodes()
        print(f"Discovered nodes: {nodes} and revision: {revision}")

        await registry.watch_nodes(revision + 1)

    finally:
        await registry.close()


def main():
    asyncio.run(serve())


if __name__ == "__main__":
    main()
