import json
from dataclasses import asdict
from typing import TypeVar
from weakref import WeakKeyDictionary

from pydantic import BaseModel
from pydantic.dataclasses import dataclass as _pydantic_dataclass

from . import Block

B = TypeVar("B", bound=Block)


_block_pydantic_map: WeakKeyDictionary[
    type[Block], type[BaseModel]
] = WeakKeyDictionary()


def _register_pydantic_model(block_type: type[Block]) -> None:
    if block_type not in _block_pydantic_map:
        block_pydantic_type = _pydantic_dataclass(
            block_type, kw_only=True
        ).__pydantic_model__
        block_pydantic_type.Config.orm_mode = True
        _block_pydantic_map[block_type] = block_pydantic_type


def json_to_block(json: str | bytes, block_type: type[B]) -> B:
    if block_type not in _block_pydantic_map:
        _register_pydantic_model(block_type)
    return block_type(**_block_pydantic_map[block_type].parse_raw(json).dict())


def block_to_json(block: Block) -> str:
    if type(block) in _block_pydantic_map:
        return _block_pydantic_map[type(block)].from_orm(block).json()
    try:
        return json.dumps(asdict(block))
    except TypeError:
        _register_pydantic_model(type(block))
        return block_to_json(block)
