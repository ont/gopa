from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class Comment:
    text: str


@dataclass
class TypeSlice:
    len: int
    value: Any  # TODO: general type


@dataclass
class TypeMap:
    key: Any    # TODO: general type (but ideally must be hashable type)
    value: Any  # TODO: general type


@dataclass
class StructField:
    name: str
    type: Any
    tag: str  # nonparsed tag (backticked string `...`)


@dataclass
class TypeStruct:
    anonymous: List[Any]  # TODO: type definition
    fields: List[Any]     # TODO:


@dataclass
class TypePtr:
    to: Any  # TODO general type


@dataclass
class TypeRef:
    package: Optional[str]
    name: str


@dataclass
class Decl:
    name: str
    type: Any  # TODO general type


@dataclass
class TypeBase:
    name: str


@dataclass
class TypeChan:
    read: bool
    write: bool
    type: Any  # TODO general type


@dataclass
class FuncReceiver:
    name: str
    type: Any  # TODO general type


@dataclass
class TypeFunc:
    args: List[Any]    # TODO general type
    result: List[Any]  # TODO general type


@dataclass
class DeclFunc:
    receiver: Optional[FuncReceiver]
    name: str
    args: List[Any]    # TODO general type
    result: List[Any]  # TODO general type
    body: str
    comments: Optional[List[Comment]] = field(default_factory=list)


@dataclass
class DeclInit:
    name: str
    type: Any
    value: Any
    comments: Optional[List[Comment]] = field(default_factory=list)


@dataclass
class DeclBlock:
    name: str
    decls: List[DeclInit]
    comments: Optional[List[Comment]] = field(default_factory=list)


@dataclass
class Package:
    name: str
    comments: Optional[List[Comment]] = field(default_factory=list)
