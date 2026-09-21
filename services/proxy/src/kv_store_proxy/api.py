import asyncio

import grpc
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from . import storage_pb2
from .hash_ring import HashRing
from .registry import NodeRegistry
from .storage_client import StorageClient

app = FastAPI()


class PutBody(BaseModel):
    value: str


def get_stubs(key: str, req: Request):
    ring: HashRing = req.app.state.ring
    registry: NodeRegistry = req.app.state.registry
    storage_client: StorageClient = req.app.state.storage_client

    node_ids = ring.get_nodes(key)

    return [storage_client.get_stub(registry.nodes[node_id]) for node_id in node_ids]


async def wait_for_read_quorum(calls, quorum: int):
    tasks = [asyncio.ensure_future(call) for call in calls]

    responses = []

    for task in asyncio.as_completed(tasks):
        try:
            response = await task
            responses.append(response)

            if len(responses) >= quorum:
                return responses
        except grpc.aio.AioRpcError:
            continue

    raise HTTPException(
        status_code=503,
        detail="Read quorum not reached",
    )


async def wait_for_write_quorum(calls, quorum: int):
    tasks = [asyncio.ensure_future(call) for call in calls]

    successes = 0

    for task in asyncio.as_completed(tasks):
        try:
            await task
            successes += 1

            if successes >= quorum:
                return
        except grpc.aio.AioRpcError:
            continue

    raise HTTPException(
        status_code=503,
        detail="Write quorum not reached",
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/kv/{key}")
async def get(key: str, req: Request):
    stubs = get_stubs(key, req)
    read_quorum: int = req.app.state.read_quorum

    if len(stubs) < read_quorum:
        raise HTTPException(
            status_code=503,
            detail="Not enough replicas for read quorum",
        )

    calls = [stub.Get(storage_pb2.GetRequest(key=key)) for stub in stubs]

    responses = await wait_for_read_quorum(calls, read_quorum)

    # Temporary until version reconciliation is implemented.
    # TODO: reconcile replica responses using version metadata.
    response = next(
        (response for response in responses if response.found),
        None,
    )

    if response is None:
        raise HTTPException(status_code=404, detail="Key not found")

    return {"value": response.value}


@app.put("/kv/{key}")
async def put(key: str, body: PutBody, req: Request):
    stubs = get_stubs(key, req)
    write_quorum: int = req.app.state.write_quorum

    if len(stubs) < write_quorum:
        raise HTTPException(
            status_code=503,
            detail="Not enough replicas for write quorum",
        )

    calls = [
        stub.Put(
            storage_pb2.PutRequest(
                key=key,
                value=body.value,
            )
        )
        for stub in stubs
    ]

    await wait_for_write_quorum(calls, write_quorum)

    return {"ok": True}


@app.delete("/kv/{key}")
async def delete(key: str, req: Request):
    stubs = get_stubs(key, req)
    write_quorum: int = req.app.state.write_quorum

    if len(stubs) < write_quorum:
        raise HTTPException(
            status_code=503,
            detail="Not enough replicas for write quorum",
        )

    calls = [stub.Delete(storage_pb2.DeleteRequest(key=key)) for stub in stubs]

    await wait_for_write_quorum(calls, write_quorum)

    return {"ok": True}
