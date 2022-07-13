from rest_framework.schemas.openapi import SchemaGenerator

# class to modify the generated schema s.t. there are only get methods
class ReadOnlySchemaGenerator(SchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        paths = schema['paths']
        ro_paths = {}
        for p in paths:
            if 'get' in paths[p]:
                ro_paths[p] = {'get': paths[p]['get']}
        schema['paths'] = ro_paths
        return schema
