import importlib


class _Config:
    def __init__(self):
        self.sections = {}

    def add_section(self, section_name):
        if section_name not in self.sections:
            self.sections[section_name] = ConfigSection(self, section_name)
            setattr(self, section_name, self.sections[section_name])
        else:
            print(f"Section '{section_name}' already exists.")
            
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
                # Variable assignment case /Locals
                _content = subsection_content[1:]
                section_obj.add_section(subsection_name)
                setattr(section_obj, subsection_name, _locals[_content])

            elif isinstance(subsection_content, str) and subsection_name.startswith("@"):
                # Import case
                print("trying to import ",subsection_name[1:])
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
                print(subsection_name)
                section_obj.add_section(subsection_name)
                # Object reference case
                setattr(getattr(section_obj, subsection_name),
                        subsection_name, subsection_content)
            # print(section_obj, subsection_name, subsection_content)

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
                self.populate_section(getattr(self, section_name), section_content, _locals)
        for i,o in self.sections.items():
            print(i, o)

    def inspect_config_section(self, section_obj, indentation=""):
        for attr_name in dir(section_obj):
            if not attr_name.startswith("__"):  # Skip private attributes
                attr_value = getattr(section_obj, attr_name)
                attr_type = type(attr_value).__name__
                print(f"{indentation}{attr_name}: {attr_type}")

                if isinstance(attr_value, ConfigSection):
                    self.inspect_config_section(attr_value, indentation + "  ")


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
            print(f"Sub-section '{subsection_name}' already exists.")


Config = _Config()


config_structure = {
    "paths": {
        "#_app_dir": "emma/common/json/app_directory.json",
        "#_command_dir": f"emma/common/json/command_directory.json",
        "#_web_dir": "emma/common/json/web_sites.json",
        "#_extensions": "emma/common/json/extension.json",
        "#_command_sch": "emma/common/json/command_schema.json",
        "#_globals": "emma/common/json/globals.json",
        "#_visual_frontalface": "emma/common/assets/models/visual/haarcascade/haarcascade_frontalface_default.xml",
        "#_vosk_en": "emma/common/assets/models/vosk_models/en-model",
        "#_vosk_es": "emma/common/assets/models/vosk_models/es-model"
    },

    "tools": {
        "@converters": "emma.tools.converters.local.kit.ToolKit",
        "@generators": "emma.tools.generators.local.kit.ToolKit",
        "@data": "emma.tools.data.local.kit.ToolKit",
        "@network": "emma.tools.network.ip.ToolKit"
    },

    "system": {
        "core": {
            "thread": ["emma.system.core.core_threading.ThreadHandler", ['THREAD HANDLER', None]],
            "queue": ["emma.system.core.core_queue.QueueHandler", ['QUEUE HANDLER', None]],
            "event": ["emma.system.core.core_event.EventHandler", ['EVENT HANDLER', None, '$system.core.queue']],
            "@_console": "emma.system.core.core_console.Console",
            "@_logger": "emma.system.core.logging.logger.Logger",
            "sys_variations": ["emma.system.sys_v.SysV", ['SYS', None, '$system.core.queue']],
        },
        "protocols": {
            "@hotkeys": "emma.system.protocols.hotkeys.HotKeys",
            "@session": "emma.system.protocols.sessions.sessions_handler.SessionsHandler"
        },
        "routers": {
            "@_router": "emma.routers._router.Router",
            "@_command": "emma.routers.command_router.CommandRouter"
        },
        "forge": ["emma.forge.builder.Builder", ["FORGE", None, ['$tools.data', '$tools.converters']]],

        "thread_instances": {},  # change on runing,
        "app": None  # reference to the complete app should be change the value on runing
    },

    "services": {
        "core": {
            "@gpt": "emma.services.integrated.gpt.GPT",
            "@api_user": "emma.services.API.user_io.app.APP",
            "@api_streaming": "emma.services.API.streaming.app.APP",
            "db": ["emma.services.integrated.db_handler.DBHandler", ['SERVICE DB', None, '$system.core.queue']]
        },
        "task": {
            "miscellaneous": ["emma.services.integrated.task.miscellaneous.MiscellaneousTask", []],
            "ost": ["emma.services.integrated.task.ost.OsTask", []],
            "web": ["emma.services.integrated.task.web.WebTask", []]
        }
    },
    "Awake": ["emma.system.awake.SystemAwake", ["AWAKE", None, '$system.core.queue', '$system.core.thread', '$system.core.event', ['$tools.data', '$services.task.miscellaneous']]]

}

# Populate the configuration instance with the defined structure
Config.auto_populate_config(config_structure)

if __name__ == "__main__":
    pass
    # config.auto_populate_config(structure)
