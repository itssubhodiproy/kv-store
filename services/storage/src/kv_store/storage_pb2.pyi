from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class GetResponse(_message.Message):
    __slots__ = ("found", "value", "version", "deleted")
    FOUND_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    found: bool
    value: str
    version: int
    deleted: bool
    def __init__(self, found: _Optional[bool] = ..., value: _Optional[str] = ..., version: _Optional[int] = ..., deleted: _Optional[bool] = ...) -> None: ...

class PutRequest(_message.Message):
    __slots__ = ("key", "value", "version")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    version: int
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class PutResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ("key", "version")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    key: str
    version: int
    def __init__(self, key: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
