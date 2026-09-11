from . import storage_pb2, storage_pb2_grpc


class StorageService(storage_pb2_grpc.StorageServicer):
    def __init__(self, engine):
        self.engine = engine

    async def Get(self, request, context):
        value = self.engine.get(request.key)

        if value is None:
            return storage_pb2.GetResponse(
                found=False,
            )

        return storage_pb2.GetResponse(
            found=True,
            value=value,
        )

    async def Put(self, request, context):
        self.engine.put(
            request.key,
            request.value,
        )

        return storage_pb2.PutResponse()

    async def Delete(self, request, context):
        self.engine.delete(request.key)

        return storage_pb2.DeleteResponse()