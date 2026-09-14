import base64

import httpx


class NodeRegistry:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint.rstrip("/")
        self.client = httpx.AsyncClient()

    async def get_nodes(self):
        prefix = "/nodes/"

        response = await self.client.post(
            f"{self.endpoint}/v3/kv/range",
            json={
                "key": self._encode(prefix),
                "range_end": self._encode("/nodes0"),
            },
        )
        response.raise_for_status()

        data = response.json()

        nodes = {}

        for item in data.get("kvs", []):
            key = self._decode(item["key"])
            address = self._decode(item["value"])

            node_id = key.removeprefix(prefix)
            nodes[node_id] = address

        return nodes

    async def close(self):
        await self.client.aclose()

    @staticmethod
    def _encode(value: str):
        return base64.b64encode(value.encode()).decode()

    @staticmethod
    def _decode(value: str):
        return base64.b64decode(value.encode()).decode()
