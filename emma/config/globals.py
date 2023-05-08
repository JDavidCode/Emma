import importlib
import sys


class EMMA_GLOBALS:
    def __init__(self):
        self.task_module = importlib.import_module("emma.task_module")
        self.sys_v = importlib.import_module("emma.sys_v")
        self.interfaces_db = importlib.import_module("emma.interfaces.db")
        self.interfaces_cam_module = importlib.import_module(
            "emma.interfaces.cam_module")
        self.interfaces_listening = importlib.import_module(
            "emma.interfaces.comunication._listening")
        self.interfaces_talking = importlib.import_module(
            "emma.interfaces.comunication._talking")
        self.web_server = importlib.import_module("emma.web_server.app")

        self.tools_converters = importlib.import_module(
            "emma.tools.converters.local.kit")
        self.tools_generators = importlib.import_module(
            "emma.tools.generators.local.kit")
        self.tools_data = importlib.import_module("emma.tools.data.local.kit")

        self.run()

    def run(self):
        global task_msc, task_os, task_web
        task_msc = self.task_module.MiscellaneousModule
        task_os = self.task_module.OsModule
        task_web = self.task_module.WebModule

        global sys_v_sa, sys_v_mp, sys_v_bp, sys_v_tm, sys_v_tm_cm, sys_v_tm_qm, sys_v_cm
        sys_v_tm = self.sys_v.ThreadManager()
        sys_v_tm_qm = self.sys_v.ThreadManager.QueueManager()
        sys_v_tm_cm = self.sys_v.ThreadManager.ConsoleManager(sys_v_tm_qm)
        sys_v_cm = self.sys_v.CommandsManager
        sys_v_sa = self.sys_v.SystemAwake()
        sys_v_mp = self.sys_v.MainProcess()
        sys_v_bp = self.sys_v.BackgroundProcess(sys_v_tm_qm, sys_v_tm_cm)

        global interfaces_db_lg, interfaces_db_dt
        interfaces_db_lg = self.interfaces_db.Login
        interfaces_db_dt = self.interfaces_db.EmmaData

        global interfaces_cam_ec, interfaces_cam_fr
        interfaces_cam_ec = self.interfaces_cam_module.EmmaCamera
        interfaces_cam_fr = self.interfaces_cam_module.FacialRecognizer

        global interfaces_comunication_lg, interfaces_comunication_tg
        interfaces_comunication_lg = self.interfaces_listening.VoiceListener
        interfaces_comunication_tg = self.interfaces_talking.Talking

        global web_server
        web_server = self.web_server.WebApp

        global tools_cs, tools_gs, tools_da
        tools_cs = self.tools_converters.ToolKit
        tools_gs = self.tools_generators.ToolKit
        tools_da = self.tools_data.ToolKit

        global thread_instances
        thread_instances = None


EMMA_GLOBALS()
