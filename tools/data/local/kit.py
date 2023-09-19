import json
import os
import re
import yaml


class ToolKit:
    def __init__(self):
        pass

    def yaml_loader(path, i=None):
        with open(path, "r") as file:
            data = yaml.safe_load(file)
            if i != None:
                data = data.get(i, {})
        return data

    def yaml_saver(path, data):
        with open(path, "w") as file:
            yaml.dump(data, file)

    def create_json_file(custom_route,filename, data):
        try:
            filepath = os.path.join(custom_route, filename)
            with open(filepath, 'w') as file:
                json.dump(data, file)
            # Open the file in write mode

            return True, f"JSON file '{filename}' created successfully."
        except Exception as e:
            return False, f"Failed to create JSON file: {e}"

    def json_loader(path, i=None, json_type="dict", console_output=None):
        with open(path) as f:
            direct = json.load(f)

        if json_type == "command":
            for key, value in direct.items():
                if key == i or key in i:
                    value['key'] = key
                    return value

            return None, None

        if json_type == "list" and i is None:
            dictionary = direct  # all the json
        elif json_type == "dict" and i is None:
            dictionary = direct  # all the json
        elif json_type == "list":
            dictionary = direct.get(i, [])
        elif json_type == "dict":
            dictionary = direct.get(i, {})
        else:
            return None

        return dictionary

    def get_filename_target(filename):
        index = filename.split('.')[0]
        return index

    def format_target(filename, pandoc):
        if pandoc:
            formats = ToolKit.jsonLoader(
                "assets\\json\\extensions.json", "PANDOC_FORMATS", "list")
        else:
            formats = ToolKit.jsonLoader(
                "assets\\json\\extensions.json", "FORMATS", "dict")

        for format in formats:
            if filename.endswith(f".{format}"):
                return format

        print("The target does not have a supported or recognized format.")
        return 0

    def string_symbol_clearer(index):
        index = index.replace("'", "")
        return index

    def string_voids_clearer(index):
        index = index.lstrip()
        return index

    def item_list_remover(index, lst):
        if index in lst:
            lst.remove(index)
        return lst


if __name__ == "__main__":
    pass
