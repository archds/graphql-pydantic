from enum import Enum
from functools import singledispatch
from typing import Union, List

from pydantic import create_model, BaseModel

from core.gql_type import GQLField, GQLType, GQLEnum, GQLUnion
from utils import SCALAR


class GQL(BaseModel):
    pass


def get_type_hint(field: GQLField) -> str:
    hint = field.type
    if hint in SCALAR:
        hint = SCALAR[hint]

    if not field.required:
        hint = f'Optional[{hint}]'

    if field.is_list:
        hint = f'List[{hint}]'

    if not field.list_required and field.is_list:
        hint = f'Optional[{hint}]'

    return hint


@singledispatch
def convert_to_model(gql_type: GQLType) -> Union[BaseModel, Enum]:
    return create_model(
        gql_type.name,
        **{
            field.name: (get_type_hint(field), ... if field.required or field.list_required else None)
            for field in gql_type.fields
        },
        __base__=GQL
    )


@convert_to_model.register
def _(gql_union: GQLUnion) -> BaseModel:
    hint = ', '.join(field.name for field in gql_union.fields)
    return create_model(
        gql_union.name,
        fields=(f'Union[{hint}]', ...),
        __base__=GQL
    )


@convert_to_model.register
def _(gql_enum: GQLEnum) -> Enum:
    return Enum(gql_enum.name, gql_enum.fields)


def convert_to_models(gql_objects: List[GQLType]) -> List[BaseModel]:
    return [
        convert_to_model(gql_object)
        for gql_object in gql_objects
    ]
