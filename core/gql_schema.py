from functools import singledispatch
from pathlib import Path
from typing import List, Union

from graphql.language import (
    parse,
    TypeDefinitionNode,
    ObjectTypeDefinitionNode,
    FieldDefinitionNode,
    NonNullTypeNode,
    ListTypeNode,
    InputObjectTypeDefinitionNode,
    EnumTypeDefinitionNode,
    UnionTypeDefinitionNode,
    DocumentNode
)

from core.gql_type import GQLField, GQLType, GQLInput, GQLEnum, GQLUnion, GQLObject
from utils import get_name, get_field_typename

__all__ = ['get_gql_objects']
AST: DocumentNode = None


def parse_ast(schema: Union[str, Path]) -> DocumentNode:
    with open(schema, 'r', encoding='UTF-8') as schema_file:
        return parse(schema_file.read())


def get_node(name: str) -> TypeDefinitionNode:
    for definition in AST.definitions:
        if get_name(definition) == name:
            return definition


def convert_field(field: FieldDefinitionNode):
    field_params = {
        'name': get_name(field),
        'required': False,
        'list': False,
        'list_required': False
    }

    if isinstance(field.type, NonNullTypeNode):
        field_params['required'] = True
        field = field.type

    if isinstance(field.type, ListTypeNode):
        field_params['list'] = True
        field = field.type

        field_params['list_required'] = field_params['required']
        field_params['required'] = False

    if isinstance(field.type, NonNullTypeNode):
        field_params['required'] = True
        field = field.type

    typename = get_field_typename(field)

    return GQLField(
        name=field_params['name'],
        type=typename,
        required=field_params['required'],
        is_list=field_params['list'],
        list_required=field_params['list_required']
    )


@singledispatch
def convert_type(def_node: TypeDefinitionNode) -> GQLType:
    pass


@convert_type.register(ObjectTypeDefinitionNode)
def _(def_node: ObjectTypeDefinitionNode) -> GQLObject:
    return GQLObject(
        name=get_name(def_node),
        fields=[
            convert_field(field)
            for field in def_node.fields
        ]
    )


@convert_type.register(InputObjectTypeDefinitionNode)
def _(def_node: InputObjectTypeDefinitionNode) -> GQLInput:
    return GQLInput(
        name=get_name(def_node),
        fields=[
            convert_field(field)
            for field in def_node.fields
        ]
    )


@convert_type.register(EnumTypeDefinitionNode)
def _(def_node: EnumTypeDefinitionNode):
    return GQLEnum(
        name=get_name(def_node),
        fields=[value.name.value for value in def_node.values]
    )


@convert_type.register(UnionTypeDefinitionNode)
def _(def_node: UnionTypeDefinitionNode):
    return GQLUnion(
        name=get_name(def_node),
        fields=[
            convert_type(get_node(get_name(field)))
            for field in def_node.types
        ]
    )


def get_gql_objects(schema: Union[str, Path]) -> List[GQLType]:
    global AST
    AST = parse_ast(schema)

    return [
        convert_type(definition)
        for definition in AST.definitions
        if get_name(definition) not in ['Query', 'Mutation']
    ]
