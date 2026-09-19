from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from . import storage_pb2

app = FastAPI()


class PutBody(BaseModel):
    value: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/kv/{key}")
async def get(key: str, req: Request):
    ring = req.app.state.ring
    registry = req.app.state.registry

    node_id = ring.get_node(key)

    if node_id is None:
        raise HTTPException(status_code=503, detail="No storage nodes available")

    address = registry.nodes[node_id]

    storage_client = req.app.state.storage_client

    stub = storage_client.get_stub(address)

    response = await stub.Get(storage_pb2.GetRequest(key=key))

    if not response.found:
        raise HTTPException(status_code=404, detail="Key not found")

    return {"value": response.value}


@app.put("/kv/{key}")
async def put(key: str, body: PutBody, req: Request):
    ring = req.app.state.ring
    registry = req.app.state.registry
    storage_client = req.app.state.storage_client
    
    node_id = ring.get_node(key)

    if node_id is None:
        raise HTTPException(status_code=503, detail="No storage nodes available")

    address = registry.nodes[node_id]
    stub = storage_client.get_stub(address)

    await stub.Put(storage_pb2.PutRequest(key=key, value=body.value))

    return {"ok": True}


@app.delete("/kv/{key}")
async def delete(key: str, req: Request):
    ring = req.app.state.ring
    registry = req.app.state.registry
    storage_client = req.app.state.storage_client
    
    node_id = ring.get_node(key)

    if node_id is None:
        raise HTTPException(status_code=503, detail="No storage nodes available")

    address = registry.nodes[node_id]
    stub = storage_client.get_stub(address)

    await stub.Delete(storage_pb2.DeleteRequest(key=key))

    return {"ok": True}
