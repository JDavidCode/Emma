

import os
import platform
import shutil
import subprocess
from app.config.config import Config


class OsTask:
    def __init__(self):
        pass

    def create_symlink(self, source, link_name):
        # ... (Existing code)
        return True, link_name

    def change_file_permissions(self, path, mode):
        # ... (Existing code)
        try:
            os.chmod(path, mode)
            return True, True
        except OSError:
            return True, False

    def run_shell_script(self, script_path):
        # ... (Existing code)
        try:
            result = subprocess.run(
                ['bash', script_path], capture_output=True, text=True)
            return (True, result.stdout.strip())
        except subprocess.CalledProcessError:
            return True, ""

    def compress_directory(self, source_dir, output_filename):
        # ... (Existing code)
        return (True, output_filename + '.zip')

    def get_current_user(self):
        # ... (Existing code)
        return True, os.getlogin()

    def rename_file(self, old_path, new_name):
        # ... (Existing code)
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        os.rename(old_path, new_path)
        return True, new_path

    def delete_file_or_directory(self, path):
        # ... (Existing code)
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                return True, False
            return True, True
        except OSError:
            return True, False

    def list_subdirectories(self, path):
        # ... (Existing code)
        if os.path.exists(path) and os.path.isdir(path):
            return True, [directory for directory in os.listdir(path) if os.path.isdir(os.path.join(path, directory))]
        else:
            return True, []

    def change_working_directory(self, path):
        # ... (Existing code)
        os.chdir(path)
        return True, os.getcwd()

    def get_environment_variable(self, variable_name):
        # ... (Existing code)
        return True, os.environ.get(variable_name, "")

    def create_directory(self, path):
        # ... (Existing code)
        os.makedirs(path, exist_ok=True)
        return True, path

    def list_files_in_directory(self, path):
        # ... (Existing code)
        if os.path.exists(path) and os.path.isdir(path):
            return True, [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
        else:
            return True, []

    def copy_file(self, source, destination):
        # ... (Existing code)
        shutil.copy(source, destination)
        return True, destination

    def execute_shell_command(self, command):
        # ... (Existing code)
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True)
            return True, result.stdout.strip()
        except subprocess.CalledProcessError:
            return True, ""

    def get_system_info(self):
        # ... (Existing code)
        system_info = {
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "memory": os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024.0 ** 3),
            "disk_usage": shutil.disk_usage("/"),
        }
        return True, system_info

    def open_app(name):
        json = Config.tools.data.json_loader(
            Config.paths._app_dir, "app_dir", "dict"
        )
        for i in json.keys():
            if i == name:
                get = json.get(i)
                os.startfile(get)
                return True, f"App {i} is launching."

    def path_mover():  # Need perfoance
        return
        diccionary = Config.tools.data.json_loader(
            "assets/json/path_directory.json", "amy_paths", "dict"
        )
        downFolder = diccionary.get("downloads")
        for filename in os.listdir(downFolder):
            name, extension = os.path.splitext(downFolder + filename)

            if extension in [".jpg", ".jpeg", ".png"]:
                folder = diccionary.get("pictures")
                os.rename(downFolder + "/" + filename, folder + "/" + filename)
                print("changes have been applied")

            if extension in [".mov", ".mkv", ".mp4", ".wmv", ".flv"]:
                folder = diccionary.get("videos")
                os.rename(downFolder + "/" + filename, folder + "/" + filename)
                print("changes have been applied")

            if extension in [".wav", ".wave", ".bwf", ".aac", ".m4a", ".mp3"]:
                folder = diccionary.get("music")
                os.rename(downFolder + "/" + filename, folder + "/" + filename)
                print("changes have been applied")

            if extension in [".txt", ".docx", ".doc", ".pptx", ".ppt", "xls", ".xlsx"]:
                folder = diccionary.get("documents")
                os.rename(downFolder + "/" + filename, folder + "/" + filename)
                print("changes have been applied")

    def volume_management(action):
        # rework to linux
        return
