from pathlib import Path
from typing import Union, List, Dict

from datamodel_code_generator import InputFileType, generate, LiteralType
from pydantic.main import ModelMetaclass, BaseModel, create_model

from core.gql_model import convert_to_models
from core.gql_schema import get_gql_objects


def generate_json_schema(gql_models: List[BaseModel]) -> str:
    return create_model(
        'GQLMain',
        **{
            gql_model.__name__: (gql_model, ...)
            for gql_model in gql_models
        }
    ).schema_json(indent=2)


def generate_dict_schema(gql_models: List[BaseModel]) -> Dict:
    return create_model(
        'GQLMain',
        **{
            gql_model.__name__: (gql_model, ...)
            for gql_model in gql_models
        }
    ).schema()


def codegen_to_file(schema: Union[str, Path], result: Union[str, Path]) -> None:
    gql_objects = get_gql_objects(schema)
    gql_models = convert_to_models(gql_objects)

    for gql_model in gql_models:
        globals()[gql_model.__name__] = gql_model

    for gql_object in gql_models:
        if isinstance(gql_object, ModelMetaclass):
            gql_object.update_forward_refs(**globals())

    generate(
        generate_json_schema(gql_models),
        input_file_type=InputFileType.JsonSchema,
        output=result,
        snake_case_field=True,
        enum_field_as_literal=LiteralType.All,
        reuse_model=True
    )


if __name__ == '__main__':
    codegen_to_file(
        schema=Path.cwd() / 'schema.graphql',
        result=Path.cwd() / 'result.py'
    )
