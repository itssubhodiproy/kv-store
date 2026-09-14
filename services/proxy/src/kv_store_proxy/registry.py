import base64
import json

import httpx


class NodeRegistry:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint.rstrip("/")
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=None))
        self.nodes = {}

    async def load_nodes(self):
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

        self.nodes = {}

        for item in data.get("kvs", []):
            key = self._decode(item["key"])
            address = self._decode(item["value"])

            node_id = key.removeprefix(prefix)
            self.nodes[node_id] = address

        revision = int(data["header"]["revision"])

        return self.nodes, revision

    async def watch_nodes(self, start_revision: int):
        prefix = "/nodes/"

        payload = {
            "create_request": {
                "key": self._encode(prefix),
                "range_end": self._encode("/nodes0"),
                "start_revision": start_revision,
            }
        }

        async with self.client.stream(
            "POST", f"{self.endpoint}/v3/watch", json=payload
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)

                for event in data.get("result", {}).get("events", []):
                    event_type = event.get("type", "PUT")
                    kv = event["kv"]

                    key = self._decode(kv["key"])
                    node_id = key.removeprefix("/nodes/")

                    if event_type == "DELETE":
                        self.nodes.pop(node_id, None)
                        print(f"DELETE {node_id}")
                    else:
                        address = self._decode(kv["value"])
                        self.nodes[node_id] = address
                        print(f"PUT {node_id} -> {address}")

    async def close(self):
        await self.client.aclose()

    @staticmethod
    def _encode(value: str):
        return base64.b64encode(value.encode()).decode()

    @staticmethod
    def _decode(value: str):
        return base64.b64decode(value.encode()).decode()
