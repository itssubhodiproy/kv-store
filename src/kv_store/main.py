import asyncio

import grpc

from . import storage_pb2_grpc
from .grpc_service import StorageService
from .storage_engine import StorageEngine


async def serve():
    engine = StorageEngine()
    server = grpc.aio.server()

    storage_pb2_grpc.add_StorageServicer_to_server(
        StorageService(engine),
        server,
    )

    server.add_insecure_port("[::]:50051")

    await server.start()
    print("Storage node listening on :50051")

    await server.wait_for_termination()


def main():
    asyncio.run(serve())


if __name__ == "__main__":
    main()