import asyncio
import base64

import httpx


class NodeRegistry:
    def __init__(self, endpoint, node_id, address, ttl=10):
        self.endpoint = endpoint.rstrip("/")
        self.node_id = node_id
        self.address = address
        self.ttl = ttl

        self.lease_id = None
        self.client = httpx.AsyncClient()

    async def register(self):
        # Create lease
        response = await self.client.post(
            f"{self.endpoint}/v3/lease/grant",
            json={"TTL": self.ttl},
        )
        response.raise_for_status()

        self.lease_id = response.json()["ID"]

        # Register node and attach it to lease
        await self.client.post(
            f"{self.endpoint}/v3/kv/put",
            json={
                "key": self._encode(f"/nodes/{self.node_id}"),
                "value": self._encode(self.address),
                "lease": self.lease_id,
            },
        )

        print(f"Registered {self.node_id} -> {self.address}")

    async def keep_alive(self):
        while True:
            await asyncio.sleep(3)

            response = await self.client.post(
                f"{self.endpoint}/v3/lease/keepalive",
                json={"ID": self.lease_id},
            )
            response.raise_for_status()

    async def unregister(self):
        if self.lease_id:
            await self.client.post(
                f"{self.endpoint}/v3/lease/revoke",
                json={"ID": self.lease_id},
            )

        await self.client.aclose()

    @staticmethod
    def _encode(value):
        return base64.b64encode(value.encode()).decode()
