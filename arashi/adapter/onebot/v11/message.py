"""Onebot v11 消息类型"""

import ujson as json
from base64 import b64encode
from io import BytesIO
from pathlib import Path
from typing import Type, Tuple, Union, Iterable, Optional, Any

from arashi.internal.adapter.message import Message as CoreMessage, MessageSegment as CoreMessageSegment



def bool_to_string(boolean: Optional[bool]) -> Optional[str]:
    return boolean if boolean is None else str(boolean).lower()

def file_to_base64(file: bytes | Path | str) -> str:
    if isinstance(file, Path):
        return file.resolve().as_uri()
    
    if isinstance(file, bytes):
        return 'base64://' + b64encode(file).decode()

    return file

class MessageSegment(CoreMessageSegment):

    @staticmethod
    def text(content: str) -> "MessageSegment":
        return MessageSegment(type='text', data={'text': content})

    @staticmethod
    def at(qq: int, name: str = '') -> "MessageSegment":
        return MessageSegment(type='at', data={'qq': qq, 'name': name})

    @staticmethod
    def image(
            file: Union[str, bytes, BytesIO, Path],
            type_: Optional[str] = None,
            cache: bool = True,
            proxy: bool = True,
            timeout: Optional[int] = None,
        ) -> "MessageSegment":
            if isinstance(file, BytesIO):
                file = file.getvalue()
            if isinstance(file, bytes):
                file = file_to_base64(file)
            elif isinstance(file, Path):
                file = file.resolve().as_uri()
            return MessageSegment(
                "image",
                {
                    "file": file,
                    "type": type_,
                    "cache": bool_to_string(cache),
                    "proxy": bool_to_string(proxy),
                    "timeout": timeout,
             },
            )

    @staticmethod
    def poke(qq: str) -> "MessageSegment":
        return MessageSegment(type='poke', data={'qq': qq})

    @staticmethod
    def xml(data: str) -> "MessageSegment":
        return MessageSegment(type='xml', data={'data': data})

    @staticmethod
    def json(data: dict[str, Any]) -> "MessageSegment":
        return MessageSegment(type='json', data={'data': json.dumps(data)})


    @staticmethod
    def reply(id_: int) -> "MessageSegment":
        return MessageSegment("reply", {"id": str(id_)})

class Message(CoreMessage[MessageSegment]):
    def __init__(self, *segments: CoreMessageSegment) -> None:
        self._segments = segments
    
    @property
    def segments(self) -> tuple[MessageSegment, ...]:
        return self._segments

    @property
    def plain_text(self) -> str:
        return ''.join(seg.data['text'] for seg in self._segments if seg.type == 'text')
