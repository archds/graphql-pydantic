from typing import List, Type

from pydantic import BaseModel


class GQLScalar(BaseModel):
    type: Type


class GQLField(BaseModel):
    name: str
    type: str
    required: bool
    is_list: bool
    list_required: bool


class GQLType(BaseModel):
    name: str
    fields: List[GQLField]


class GQLObject(GQLType):
    pass


class GQLInput(GQLType):
    pass


class GQLUnion(GQLType):
    pass


class GQLEnum(GQLType):
    fields: List[str]


class GQLUnion(GQLType):
    fields: List[GQLType]
