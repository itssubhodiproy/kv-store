import asyncio
import os

import grpc

from . import storage_pb2_grpc
from .grpc_service import StorageService
from .registry import NodeRegistry
from .storage_engine import StorageEngine


async def serve():
    port = os.getenv("PORT", "50051")
    data_dir = os.getenv("DATA_DIR", "data")

    node_id = os.getenv("NODE_ID", "storage-node")
    etcd_endpoint = os.getenv(
        "ETCD_ENDPOINT",
        "http://localhost:2379",
    )

    address = f"{node_id}:{port}"

    engine = StorageEngine(data_dir=data_dir)

    server = grpc.aio.server()

    storage_pb2_grpc.add_StorageServicer_to_server(
        StorageService(engine),
        server,
    )

    server.add_insecure_port(f"[::]:{port}")

    # Become reachable first
    await server.start()

    registry = NodeRegistry(
        endpoint=etcd_endpoint,
        node_id=node_id,
        address=address,
    )

    # Then advertise ourselves
    await registry.register()

    keep_alive_task = asyncio.create_task(registry.keep_alive())

    print(f"Storage node listening on :{port}")

    try:
        await server.wait_for_termination()
    finally:
        keep_alive_task.cancel()
        await registry.unregister()


def main():
    asyncio.run(serve())


if __name__ == "__main__":
    main()
