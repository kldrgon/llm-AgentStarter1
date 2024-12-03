from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class QueryRequest(_message.Message):
    __slots__ = ("question", "file_data")
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    FILE_DATA_FIELD_NUMBER: _ClassVar[int]
    question: str
    file_data: bytes
    def __init__(self, question: _Optional[str] = ..., file_data: _Optional[bytes] = ...) -> None: ...

class QueryResponse(_message.Message):
    __slots__ = ("has_text", "text_answer", "has_image", "image_data")
    HAS_TEXT_FIELD_NUMBER: _ClassVar[int]
    TEXT_ANSWER_FIELD_NUMBER: _ClassVar[int]
    HAS_IMAGE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    has_text: bool
    text_answer: str
    has_image: bool
    image_data: bytes
    def __init__(self, has_text: bool = ..., text_answer: _Optional[str] = ..., has_image: bool = ..., image_data: _Optional[bytes] = ...) -> None: ...
