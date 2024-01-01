import importlib
import inspect
import textwrap


class ConfigSection:
    def __init__(self, config_obj, section_name):
        self.config = config_obj
        self.section_name = section_name
        self.subsections = {}

    def add_section(self, subsection_name):
        if subsection_name not in self.subsections:
            self.subsections[subsection_name] = ConfigSection(
                self.config, subsection_name)
            setattr(self, subsection_name, self.subsections[subsection_name])
        else:
            print(f"error: Sub-section '{subsection_name}' already exists.")


class _Config:
    def __init__(self):
        self.sections = {}

    def add_section(self, section_name):
        if section_name not in self.sections:
            self.sections[section_name] = ConfigSection(self, section_name)
            setattr(self, section_name, self.sections[section_name])
        else:
            print(f"error: Section '{section_name}' already exists.")

    def del_all_sections(self):
        self.sections = {}
        for section_name in dir(self):
            if section_name in self.sections:
                delattr(self, section_name)

    def resolve_references(self, value, config):
        if isinstance(value, list):
            return [self.resolve_references(item, config) for item in value]
        elif isinstance(value, str) and value.startswith('$'):
            reference_key = value[1:]
            sections = reference_key.split('.')
            current_section = config
            for section in sections:
                current_section = getattr(current_section, section, None)
                if current_section is None:
                    break
            return current_section
        else:
            return value

    def populate_section(self, section_obj, content, _locals):
        for subsection_name, subsection_content in content.items():
            if isinstance(subsection_content, dict):
                section_obj.add_section(subsection_name)
                self.populate_section(
                    getattr(section_obj, subsection_name), subsection_content, _locals)

            elif isinstance(subsection_content, str) and subsection_name.startswith("#"):
                # File path or path reference case
                _name = subsection_name[1:]
                section_obj.add_section(_name)
                path_key = _name
                setattr(section_obj, path_key, subsection_content)

            elif isinstance(subsection_content, str) and subsection_content.startswith("&"):
                # Variable assignment case / Locals
                _content = subsection_content[1:]
                section_obj.add_section(subsection_name)
                setattr(section_obj, subsection_name, _locals[_content])

            elif isinstance(subsection_content, str) and subsection_name.startswith("@"):
                # Import case
                print("Population importing " + subsection_name[1:])
                _name = subsection_name[1:]
                section_obj.add_section(_name)
                module_path, class_name = subsection_content.rsplit(".", 1)
                module = importlib.import_module(module_path)
                class_obj = getattr(module, class_name)
                setattr(section_obj, _name, class_obj)

            elif isinstance(subsection_content, list) and len(subsection_content) >= 1:
                class_path = subsection_content[0]
                module_path, class_name = class_path.rsplit(".", 1)
                module = importlib.import_module(module_path)
                class_obj = getattr(module, class_name)
                if len(subsection_content) > 1:
                    instance_args = [self.resolve_references(
                        arg, self) for arg in subsection_content[1]]
                    instance = class_obj(*instance_args)
                else:
                    instance = class_obj

                setattr(section_obj, subsection_name, instance)
            else:
                print("Populating: ", subsection_name)
                section_obj.add_section(subsection_name)
                # Object reference case
                setattr(getattr(section_obj, subsection_name),
                        subsection_name, subsection_content)

    def auto_populate_config(self, structure, _locals=None):
        if _locals is None:
            _locals = locals()

        for section_name, section_content in structure.items():
            if section_content is None:
                continue
            if isinstance(section_content, list):
                class_path = section_content[0]
                module_path, class_name = class_path.rsplit(".", 1)
                module = importlib.import_module(module_path)
                class_obj = getattr(module, class_name)
                if len(section_content[1]) > 1:
                    instance_args = [self.resolve_references(
                        arg, self) for arg in section_content[1]]
                    instance = class_obj(*instance_args)
                else:
                    instance = class_obj

                setattr(self, section_name, instance)
            else:
                self.add_section(section_name)
                self.populate_section(
                    getattr(self, section_name), section_content, _locals)

    def inspect_config_section(self, section_obj, indentation=""):
        result = {}

        for attr_name in dir(section_obj):
            if not attr_name.startswith("__"):  # Skip private attributes
                attr_value = getattr(section_obj, attr_name)
                attr_type = type(attr_value).__name__

                if isinstance(attr_value, ConfigSection):
                    result[attr_name] = self.inspect_config_section(
                        attr_value, indentation + "  ")
                else:
                    result[attr_name] = {"type": attr_type}

        # Si el atributo final es una función, obtén el código fuente
        if "source_code" not in result and (type(section_obj).__name__ == "method" or type(section_obj).__name__ == "function"):
            result["source_code"] = self.get_method_source_code(section_obj)
        return result

    def get_method_source_code(self, section_obj):
        try:
            return inspect.getsource(section_obj)
        except (OSError, TypeError, ValueError, ImportError, IOError) as e:
            print(f"Error getting source code: {e}")
            return ""

    def format_source_code(source_code):
        """
        Format the source code for better readability.

        Args:
            source_code (str): The source code to format.

        Returns:
            str: Formatted source code.
        """
        # Utiliza textwrap para indentar el código fuente
        formatted_code = textwrap.dedent(source_code)
        return formatted_code


# Create a configuration instance
Config = _Config()

config_structure = {
    "paths": {
        "#_app_dir": "app/common/json/app_directory.json",
        "#_command_dir": f"app/common/json/command_directory.json",
        "#_web_dir": "app/common/json/web_sites.json",
        "#_extensions": "app/common/json/extension.json",
        "#_command_sch": "app/common/json/command_schema.json",
        "#_globals": "app/common/json/globals.json",
    },

    "tools": {
        "@converters": "tools.converters.kit.ToolKit",
        "@generators": "tools.generators.kit.ToolKit",
        "@data": "tools.data.kit.ToolKit",
        "@network": "tools.network.ip.ToolKit"
    },

    "forge": ["forge.builder.Builder", ["FORGE", None, ['$tools.data', '$tools.converters']]],

    "app": {
        "system": {
            "core": {
                "thread": ["app.system.core._threading.ThreadHandler", ['THREAD HANDLER', None]],
                "queue": ["app.system.core._queue.QueueHandler", ['QUEUE HANDLER', None]],
                "event": ["app.system.core._event.EventHandler", ['EVENT HANDLER', None, '$app.system.core.queue']],
                "@_console": "app.system.core._console.Console",
                "@_logger": "app.system.core.logging.logger.Logger",

            },

            "admin": {
                "agents": {
                    "@withelist": ["app.system.admin.agents.system._withelist.WhitelistAgent"],
                    "sys": ["app.system.admin.agents.system._system.SystemManager", ['SYS AGENT', None, '$app.system.core.queue']],
                    "@db": "app.system.admin.agents.database._db.DatabaseAgent",
                    "user": ["app.system.admin.agents.user._usr.UserManager", ["USER AGENT"]],
                    "session": ["app.system.admin.agents.sessions._sessions.SessionsAgent", ["SESSIONS AGENT", '$app.system.core.queue', '$app.system.core.event']]

                },
                "routers": {
                    "@_input": "app.system.admin.routers._input.InputRouter",
                    "@_command": "app.system.admin.routers._command.CommandRouter"
                },
                "protocols": {
                },
            },

            "thread_instances": {},  # change on runing,
            "_app": None  # reference to the complete app should be change the value on runing
        },



        "services": {
            "core": {
                "@gpt": "app.services.gpt.GPT",
                "@api_user": "app.services.api.user_io.app.App",
                # "@api_streaming": "app.services.api.streaming.app.App",
            },
            "task": {
                "miscellaneous": ["app.services.task.miscellaneous.MiscellaneousTask", []],
                "ost": ["app.services.task.ost.OsTask", []],
                "web": ["app.services.task.web.WebTask", []]
            },
            "common": {
            }
        },
    },

    "_init": ["app.__init__.Run", ["__INIT__", None, '$app.system.core.queue', '$app.system.core.thread', '$app.system.core.event', ['$tools.data', '$app.services.task.miscellaneous']]]

}

# Populate the configuration instance with the defined structure
Config.auto_populate_config(config_structure)

if __name__ == "__main__":
    pass  # Add your application logic here
