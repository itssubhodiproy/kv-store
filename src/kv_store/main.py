import asyncio
import os

import grpc

from . import storage_pb2_grpc
from .grpc_service import StorageService
from .storage_engine import StorageEngine


async def serve():
    port = os.getenv("PORT", "50051")
    data_dir = os.getenv("DATA_DIR", "data")

    engine = StorageEngine(data_dir=data_dir)
    server = grpc.aio.server()

    storage_pb2_grpc.add_StorageServicer_to_server(
        StorageService(engine),
        server,
    )

    server.add_insecure_port(f"[::]:{port}")

    await server.start()
    print(f"Storage node listening on :{port}")

    await server.wait_for_termination()


def main():
    asyncio.run(serve())


if __name__ == "__main__":
    main()
