import importlib
import os
import traceback
# Las 'Instancias' de las clases que se ejecuran un thread no se les debe pasar argumentos, esto se hara en sys_initialize thread automaticamente, solo dejar la referencia de la clase


class EMMA_GLOBALS:
    def __init__(self):
        self.sys_awake = importlib.import_module("emma.system.awake")
        self.tools_instances()
        self.sys_awake.SystemAwake(fase=0, tools=tools_da)
        self.variables()
        self.system()
        self.services()
        self.instances()
        

    

    def tools_instances(self):
        tools_converters = importlib.import_module(
            "emma.tools.converters.local.kit"
        )
        tools_generators = importlib.import_module(
            "emma.tools.generators.local.kit"
        )
        tools_data = importlib.import_module("emma.tools.data.local.kit")
        tools_network = importlib.import_module("emma.tools.network.ip")

        global tools_cs, tools_gs, tools_da, tools_net
        tools_cs = tools_converters.ToolKit
        tools_gs = tools_generators.ToolKit
        tools_da = tools_data.ToolKit
        tools_net = tools_network.ToolKit

    def variables(self):
        global stcpath_app_dir, stcpath_command_dir, stcpath_web_dir, stcpath_extensions, stcpath_command_sch,stcpath_globals
        stcpath_app_dir = "emma/common/json/app_directory.json"
        stcpath_command_dir = f"emma/common/json/command_directory-{os.environ.get('USERLANG')}.json"
        stcpath_web_dir = "emma/common/json/web_sites.json"
        stcpath_extensions = "emma/common/json/extension.json"
        stcpath_command_sch = "emma/common/json/command_schema.json"
        stcpath_globals= "emma/common/json/globals.json"

        global stcmodel_visual_frontalface, stcmode_vosk_en, stcmode_vosk_es
        stcmodel_visual_frontalface = (
            "emma/common/assets/models/visual/haarcascade/haarcascade_frontalface_default.xml"
        )
        stcmode_vosk_en = "emma/common/assets/models/vosk_models/en-model"
        stcmode_vosk_es = "emma/common/assets/models/vosk_models/es-model"

    class system:
        def __init__(self) -> None:
            self.main()
            self.logger()
            self.protocols()

        def main(self):
            sys_variations = importlib.import_module("emma.system.sys_v")
            core = importlib.import_module("emma.system.core_threading")

            global core_thread_handler, core_queue_handler, core_console_handler, core_event_handler, sys_v

            core_thread_handler = core.ThreadHandler()
            core_queue_handler = core.QueueHandler()
            core_console_handler = core.ConsoleHandler(core_queue_handler)
            core_event_handler = core.EventHandler(core_console_handler)
            sys_v = sys_variations.SysV(core_queue_handler, core_console_handler)


        def protocols(self):
            prt_session = importlib.import_module(
                "emma.system.protocols.sessions.sessions_handler")

            global session_protocols
            session_protocols = prt_session.SessionsHandler
        
        def logger(self):
            _logger = importlib.import_module("emma.system.logging.logger")

            global logger
            logger= _logger.Logger


        def network(self):
            pass

    class services:
        def __init__(self) -> None:
            self.main()
            self.common()
            self.task()

        def main(self):
            _services_gpt = importlib.import_module(
                "emma.services.integrated.gpt"
            )
            # self.services_tts = importlib.import_module("emma.services.integrated.tts")
            # services_tts = self.services_tts.TTS(core_console_handler)
            _services_api_user_io = importlib.import_module(
                "emma.services.API.user_io.app")
            _services_db = importlib.import_module(
                "emma.services.integrated.db_handler")

            global services_db, services_gpt, services_api_user_io        # , services_tts

            services_db = _services_db.DBHandler(core_queue_handler, core_console_handler)
            services_gpt = _services_gpt.GPT

            services_api_user_io = _services_api_user_io.APP

        def common(self):
            _geolocation_module = importlib.import_module(
                "emma.services.integrated.common.geolocation")
            _time_module = importlib.import_module(
                "emma.services.integrated.common.time")
            _weather_module = importlib.import_module(
                "emma.services.integrated.common.weather")

            global service_geolocation, service_time, service_weather
            service_geolocation = _geolocation_module.GeoLocationService
            service_time = _time_module.TimeService
            service_weather = _weather_module.WeatherService

        def task(self):
            _miscellaneous_module = importlib.import_module(
                "emma.services.integrated.task.miscellaneous")
            _ost_module = importlib.import_module(
                "emma.services.integrated.task.ost")
            _web_module = importlib.import_module(
                "emma.services.integrated.task.web")

            global task_msc, task_os, task_web

            task_msc = _miscellaneous_module.MiscellaneousTask
            task_os = _ost_module.OsTask
            task_web = _web_module.WebTask

    def instances(self):
        i_router = importlib.import_module(
            "emma.system.routers.input_router")
        cmmand_router = importlib.import_module(
            "emma.system.routers.command_router")
        forge = importlib.import_module("emma.forge.builder")

        global command_router, io_router, sys_awake, forge_server, thread_instances

        sys_awake = self.sys_awake.SystemAwake(
            1, core_console_handler, core_queue_handler, core_thread_handler, core_event_handler, tools_da)
        command_router = cmmand_router.CommandRouter
        io_router = i_router.InputRouter
        thread_instances = {}
        forge_server = forge.Builder([tools_cs, tools_da])


class FORGE_GLOBALS:
    def __init__(self):
        self.variables()

    def variables(self):
        # here some needed varibales ignore them
        pass

    def create_instance(self, package_name, endpoint):
        package = importlib.import_module(
            f"emma.services.external.{package_name}.{endpoint}"
        )
        global_namespace = globals()
        global_variable_name = f"forge_package_{package_name}"
        try:
            global_namespace[global_variable_name] = getattr(package, endpoint)
        except Exception as e:
            print(f"Error creating instance of {package_name}: {e}")

def recreate_reloaded_module(module_name):
    diccionary = tools_da.json_loader(
                stcpath_globals)
    key = diccionary.keys()

    for i in key:
        if module_name in i:
            module_info = diccionary.get(i)
            endpoint = module_info.get("endpoint")
            module_path = module_info.get("path")
            args = module_info.get("args")
            isinsta= module_info.get("instance")
            args = [eval(arg) for arg in args]

            try:
                # Load the module dynamically based on its path
                module = importlib.import_module(module_path)

                # Create a new instance of the reloaded module with the given arguments

                if eval(isinsta) and args != []:
                    new_instance = getattr(module, endpoint)(*args)
                elif eval(isinsta):
                    new_instance = getattr(module, endpoint)()
                else:
                    new_instance = getattr(module, endpoint)

                # Replace the old instance with the new on
                global_namespace = globals()
                global_namespace[module_name] = new_instance

                
                return True, f"Instance {module_name} of module {module_name} has been reloaded."
            except Exception as e:
                traceback_str = traceback.format_exc()
                core_queue_handler.add_to_queue("LOGGING", ("RECREATE INSTANCE", [f"Error recreating instance of {module_name}: {e}", traceback_str]))
                return False, traceback_str
                
EMMA_GLOBALS()
