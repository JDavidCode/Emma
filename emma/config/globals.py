import importlib
import os
import sys


class EMMA_GLOBALS:
    def __init__(self):
        self.sys_v = importlib.import_module("emma.sys_v")
        self.tools_instances()
        self.sys_v.SystemAwake(fase=0, tools=tools_da)

        self.variables()
        self.services_db = importlib.import_module(
            "emma.services.integrated.db")
        self.services_cam_module = importlib.import_module(
            "emma.services.integrated.cam_module"
        )
        self.services_listening = importlib.import_module(
            "emma.services.integrated.comunication._listening"
        )
        self.services_talking = importlib.import_module(
            "emma.services.integrated.comunication._talking"
        )
        self.forge_server = importlib.import_module("emma.forge.builder")
        self.task_module = importlib.import_module("emma.task_module")

        self.instances()

    def variables(self):
        global stcpath_app_dir, stcpath_command_dir, stcpath_module_dir, stcpath_web_dir, stcpath_extensions
        stcpath_app_dir = "emma/assets/json/app_directory.json"
        stcpath_command_dir = f"emma/assets/json/command_directory-{os.environ.get('USERLANG')}.json"
        stcpath_module_dir = "emma/assets/json/module_directory.json"
        stcpath_web_dir = "emma/assets/json/web_sites.json"
        stcpath_extensions = "emma/assets/json/extension.json"

        global stcmodel_visual_frontalface, stcmode_vosk_en, stcmode_vosk_es
        stcmodel_visual_frontalface = (
            "emma/assets/models/visual/haarcascade/haarcascade_frontalface_default.xml"
        )
        stcmode_vosk_en = "emma/assets/models/vosk_models/en-model"
        stcmode_vosk_es = "emma/assets/models/vosk_models/es-model"

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

        global sys_v_th, sys_v_th_ch, sys_v_th_qh, sys_v_th_eh, sys_v_cm, sys_v_sa, sys_v
        sys_v_th = self.sys_v.ThreadHandler()
        sys_v_th_qh = self.sys_v.ThreadHandler.QueueHandler()
        sys_v_th_ch = self.sys_v.ThreadHandler.ConsoleHandler(sys_v_th_qh)
        sys_v_th_eh = self.sys_v.ThreadHandler.EventHandler()
        sys_v_cm = self.sys_v.CommandsManager
        sys_v_sa = self.sys_v.SystemAwake(1,
                                          sys_v_th_ch, sys_v_th_qh, sys_v_th, sys_v_th_eh, tools_da)
        sys_v = self.sys_v.SysV(sys_v_th_qh, sys_v_th_ch)

        global services_db_lg, services_db_dt
        services_db_lg = self.services_db.Login
        services_db_dt = self.services_db.EmmaData

        global services_cam_ec, services_cam_fr
        services_cam_ec = self.services_cam_module.EmmaCamera
        services_cam_fr = self.services_cam_module.FacialRecognizer

        global services_comunication_lg, services_comunication_tg
        services_comunication_lg = self.services_listening.VoiceListener
        services_comunication_tg = self.services_talking.Talking

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
