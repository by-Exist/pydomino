import json
from dataclasses import asdict, is_dataclass
from typing import Any
from weakref import WeakKeyDictionary

from pydantic import BaseModel
from pydantic.dataclasses import dataclass as pydantic_dataclass

D = Any


_dataclass_pydantic_map: WeakKeyDictionary[
    type[D], type[BaseModel]
] = WeakKeyDictionary()


def _register_pydantic_model(dataclass: type[D]) -> None:
    assert is_dataclass(dataclass)
    if dataclass not in _dataclass_pydantic_map:
        block_pydantic_type = pydantic_dataclass(
            dataclass, kw_only=True
        ).__pydantic_model__
        block_pydantic_type.Config.orm_mode = True
        _dataclass_pydantic_map[dataclass] = block_pydantic_type


def json_to_data(json: str | bytes, dataclass: type[D]) -> D:
    if dataclass not in _dataclass_pydantic_map:
        _register_pydantic_model(dataclass)
    return dataclass(**_dataclass_pydantic_map[dataclass].parse_raw(json).dict())


def data_to_json(data: Any) -> str:
    if type(data) in _dataclass_pydantic_map:
        return _dataclass_pydantic_map[type(data)].from_orm(data).json()
    try:
        return json.dumps(asdict(data))
    except TypeError:
        _register_pydantic_model(type(data))
        return data_to_json(data)
