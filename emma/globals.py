import importlib
import os
import sys
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
        global stcpath_app_dir, stcpath_command_dir, stcpath_module_dir, stcpath_web_dir, stcpath_extensions, stcpath_command_sch
        stcpath_app_dir = "emma/common/json/app_directory.json"
        stcpath_command_dir = f"emma/common/json/command_directory-{os.environ.get('USERLANG')}.json"
        stcpath_module_dir = "emma/common/json/module_directory.json"
        stcpath_web_dir = "emma/common/json/web_sites.json"
        stcpath_extensions = "emma/common/json/extension.json"
        stcpath_command_sch = "emma/common/json/command_schema.json"

        global stcmodel_visual_frontalface, stcmode_vosk_en, stcmode_vosk_es
        stcmodel_visual_frontalface = (
            "emma/common/assets/models/visual/haarcascade/haarcascade_frontalface_default.xml"
        )
        stcmode_vosk_en = "emma/common/assets/models/vosk_models/en-model"
        stcmode_vosk_es = "emma/common/assets/models/vosk_models/es-model"

    class system:
        def __init__(self) -> None:
            self.main()
            self.protocols()

        def main(self):
            sys = importlib.import_module("emma.system.sys_v")

            global sys_v_th, sys_v_th_ch, sys_v_th_qh, sys_v_th_eh, sys_v

            sys_v_th = sys.ThreadHandler()
            sys_v_th_qh = sys.ThreadHandler.QueueHandler()
            sys_v_th_ch = sys.ThreadHandler.ConsoleHandler(sys_v_th_qh)
            sys_v_th_eh = sys.ThreadHandler.EventHandler()
            sys_v = sys.SysV(sys_v_th_qh, sys_v_th_ch)

        def protocols(self):
            prt_session = importlib.import_module(
                "emma.system.protocols.sessions.sessions_handler")

            global session_protocols
            session_protocols = prt_session.SessionsHandler

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
            # services_tts = self.services_tts.TTS(sys_v_th_ch)
            _services_api_user_io = importlib.import_module(
                "emma.services.API.user_io.app")
            _services_db = importlib.import_module(
                "emma.services.integrated.db_connection")

            global services_db, services_gpt, services_api_user_io        # , services_tts

            services_db = _services_db.DBHandler(sys_v_th_qh, sys_v_th_ch)
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
            1, sys_v_th_ch, sys_v_th_qh, sys_v_th, sys_v_th_eh, tools_da)
        command_router = cmmand_router.CommandsRouter
        io_router = i_router.InputRouter
        thread_instances = None
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


EMMA_GLOBALS()
