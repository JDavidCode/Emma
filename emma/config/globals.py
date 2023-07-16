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
        self.sys_v = importlib.import_module("emma.system.sys_v")

        self.services_db = importlib.import_module(
            "emma.services.integrated.db")

        self.services_gpt = importlib.import_module(
            "emma.services.integrated.gpt"
        )
        self.services_tts = importlib.import_module(
            "emma.services.integrated.tts"
        )
        self.services_api_user_io = importlib.import_module(
            "emma.services.API.user_io.app"
        )
        self.forge_server = importlib.import_module("emma.forge.builder")
        self.task_module = importlib.import_module("emma.system.task_module")

        self.instances()

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

    def tools_instances(self):
        self.tools_converters = importlib.import_module(
            "emma.tools.converters.local.kit"
        )
        self.tools_generators = importlib.import_module(
            "emma.tools.generators.local.kit"
        )
        self.tools_data = importlib.import_module("emma.tools.data.local.kit")

        global tools_cs, tools_gs, tools_da
        tools_cs = self.tools_converters.ToolKit
        tools_gs = self.tools_generators.ToolKit
        tools_da = self.tools_data.ToolKit

    def instances(self):
        global task_msc, task_os, task_web
        task_msc = self.task_module.MiscellaneousModule
        task_os = self.task_module.OsModule
        task_web = self.task_module.WebModule

        global sys_v_th, sys_v_th_ch, sys_v_th_qh, sys_v_th_eh, sys_v_cm, sys_v_ir, sys_awake, sys_v
        sys_v_th = self.sys_v.ThreadHandler()
        sys_v_th_qh = self.sys_v.ThreadHandler.QueueHandler()
        sys_v_th_ch = self.sys_v.ThreadHandler.ConsoleHandler(sys_v_th_qh)
        sys_v_th_eh = self.sys_v.ThreadHandler.EventHandler()
        sys_v_cm = self.sys_v.CommandsManager
        sys_v_ir = self.sys_v.InputRouter
        sys_awake = self.sys_awake.SystemAwake(
            1, sys_v_th_ch, sys_v_th_qh, sys_v_th, sys_v_th_eh, tools_da)
        sys_v = self.sys_v.SysV(sys_v_th_qh, sys_v_th_ch)

        global services_db_lg, services_db_dt
        services_db_lg = self.services_db.Login
        services_db_dt = self.services_db.EmmaData

        global services_gpt, services_tts
        services_tts = self.services_tts.TTS(sys_v_th_ch)
        services_gpt = self.services_gpt.GPT

        global services_api_user_io
        services_api_user_io = self.services_api_user_io.APP

        global forge_server
        forge_server = self.forge_server.Builder([tools_cs, tools_da])

        global thread_instances
        thread_instances = None


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
