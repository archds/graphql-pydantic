from operator import attrgetter

SCALAR = {
    'String': 'str',
    'Float': 'float',
    'Int': 'int',
    'ID': 'str',
    'Boolean': 'bool'
}

get_name = attrgetter('name.value')
get_field_typename = attrgetter('type.name.value')
