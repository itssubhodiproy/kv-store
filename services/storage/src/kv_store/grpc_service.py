from . import storage_pb2, storage_pb2_grpc
from .memtable import TOMBSTONE


class StorageService(storage_pb2_grpc.StorageServicer):
    def __init__(self, engine):
        self.engine = engine

    async def Get(self, request, context):
        result = self.engine.get(request.key)

        if result is None:
            return storage_pb2.GetResponse(
                found=False,
            )

        value, version = result

        if value is TOMBSTONE:
            return storage_pb2.GetResponse(found=True, deleted=True, version=version)

        return storage_pb2.GetResponse(
            found=True, value=value, version=version, deleted=False
        )

    async def Put(self, request, context):
        self.engine.put(request.key, request.value, request.version)

        return storage_pb2.PutResponse()

    async def Delete(self, request, context):
        self.engine.delete(request.key, request.version)

        return storage_pb2.DeleteResponse()
