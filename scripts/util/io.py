import json

import logging
LOGGER = logging.getLogger(__name__)


# class YamlDeserializable(object):
#     @classmethod
#     def from_yaml(cls, constructor, node):
#         data = CommentedMap()
#         constructor.construct_mapping(node, data, deep=True)
#         return cls(*node.value.split('-'))


# class YamlSerializable(object):
#     @classmethod
#     def to_yaml(cls, representer, node):
#         return representer.represent_scalar(
#                   cls.yaml_tag, u'{.name}-{.age}'.format(node, node))


class JsonSerializable(object):
    @classmethod
    def to_json(cls):
        return json.dumps(
            cls.export_data, default=lambda o: o.__dict__, indent=2)

# class JsonDeserializable(object):
#     @classmethod
#     def from_json(self):


class Importable(object):
    def __init__(self):
        pass

    def import_from_file(self, file_name, file_type):
        """ Import data from a file

        Args:
            file_name (str): file name part of a file
            file_type (str): file type part of a file
        """

        LOGGER.debug(f"Opening {file_name}.{file_type} ...")

        if file_type == "yaml":
            self.import_type = "yaml"
            with open(f"{file_name}.{file_type}", 'r') as handle:
                self.import_data = self.yaml.load(
                    handle)

        if file_type == "json":
            self.import_type = "json"
            with open(f"{file_name}.{file_type}", 'r') as handle:
                self.import_data = json.loads(
                    handle.read(), object_hook=lambda d: self.__class__(**d))


class Exportable(object):
    def __init__(self):
        pass

    def export_to_file(self, file_name, file_type):
        """ Export data to file

        Args:
            file_name (str): file name part of a file
            file_type (str): file type part of a file
        """

        LOGGER.debug(f"Writing to {file_name}.{file_type} ...")

        if file_type == "yaml":
            with open(f"{file_name}.{file_type}", 'w') as handle:
                self.yaml.dump(self.export_data, handle)
        if file_type == "json":
            # TODO: check for import type?
            with open(f"{file_name}.{file_type}", 'w') as handle:
                handle.write(self.to_json())
