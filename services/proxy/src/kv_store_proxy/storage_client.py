import grpc

from . import storage_pb2_grpc


class StorageClient:
    def __init__(self):
        self.channels = {}
        self.stubs = {}

    def get_stub(self, address: str):
        if address not in self.stubs:
            channel = grpc.aio.insecure_channel(address)

            self.channels[address] = channel
            self.stubs[address] = storage_pb2_grpc.StorageStub(channel)

        return self.stubs[address]

    async def close(self):
        for channel in self.channels.values():
            await channel.close()
