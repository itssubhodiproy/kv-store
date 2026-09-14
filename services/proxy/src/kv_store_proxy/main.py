import asyncio
import os

from .registry import NodeRegistry


async def serve():
    etcd_endpoint = os.getenv("ETCD_ENDPOINT", "http://localhost:2379")
    registry = NodeRegistry(etcd_endpoint)

    try:
        nodes = await registry.get_nodes()
        print(f"Discovered nodes; {nodes}")
    finally:
        await registry.close()


def main():
    asyncio.run(serve())


if __name__ == "__main__":
    main()
