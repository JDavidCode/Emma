

import os
import platform
import shutil
import subprocess

from emma.globals import EMMA_GLOBALS


class OsTask:
    def __init__(self):
        pass

    def create_symlink(self, source, link_name):
        """
        Create a symbolic link to a file or directory.

        Args:
            source (str): The source path of the file or directory.
            link_name (str): The name of the symbolic link to be created.

        Returns:
            str: The path of the created symbolic link.
        """
        os.symlink(source, link_name)
        return link_name

    def change_file_permissions(self, path, mode):
        """
        Change the permissions (mode) of a file or directory.

        Args:
            path (str): The path of the file or directory.
            mode (int): The new permission mode (e.g., 0o755).

        Returns:
            bool: True if the permissions were successfully changed, False otherwise.
        """
        try:
            os.chmod(path, mode)
            return True
        except OSError:
            return False

    def run_shell_script(self, script_path):
        """
        Run a shell script and return the output.

        Args:
            script_path (str): The path of the shell script to run.

        Returns:
            str: The output of the shell script as a string.
        """
        try:
            result = subprocess.run(
                ['bash', script_path], capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""

    def compress_directory(self, source_dir, output_filename):
        """
        Compress a directory into a ZIP file.

        Args:
            source_dir (str): The path of the directory to compress.
            output_filename (str): The name of the output ZIP file.

        Returns:
            str: The path of the compressed ZIP file.
        """
        shutil.make_archive(output_filename, 'zip', source_dir)
        return output_filename + '.zip'

    def get_current_user(self):
        """
        Get the username of the current user.

        Returns:
            str: The username of the current user.
        """
        return os.getlogin()

    def rename_file(self, old_path, new_name):
        """
        Rename a file or directory.

        Args:
            old_path (str): The path of the file or directory to be renamed.
            new_name (str): The new name for the file or directory.

        Returns:
            str: The new path of the renamed file or directory.
        """
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        os.rename(old_path, new_path)
        return new_path

    def delete_file_or_directory(self, path):
        """
        Delete a file or directory.

        Args:
            path (str): The path of the file or directory to be deleted.

        Returns:
            bool: True if the file or directory was successfully deleted, False otherwise.
        """
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                return False
            return True
        except OSError:
            return False

    def list_subdirectories(self, path):
        """
        List all subdirectories within the specified directory.

        Args:
            path (str): The path of the directory.

        Returns:
            list: A list of subdirectory names.
        """
        if os.path.exists(path) and os.path.isdir(path):
            return [directory for directory in os.listdir(path) if os.path.isdir(os.path.join(path, directory))]
        else:
            return []

    def change_working_directory(self, path):
        """
        Change the current working directory.

        Args:
            path (str): The path of the directory to set as the working directory.

        Returns:
            str: The path of the new working directory.
        """
        os.chdir(path)
        return os.getcwd()

    def get_environment_variable(self, variable_name):
        """
        Get the value of an environment variable.

        Args:
            variable_name (str): The name of the environment variable.

        Returns:
            str: The value of the environment variable.
        """
        return os.environ.get(variable_name, "")

    def create_directory(self, path):
        """
        Create a new directory at the specified path.

        Args:
            path (str): The path of the directory to be created.

        Returns:
            str: The path of the created directory.
        """
        os.makedirs(path, exist_ok=True)
        return path

    def list_files_in_directory(self, path):
        """
        List all files in the specified directory.

        Args:
            path (str): The path of the directory.

        Returns:
            list: A list of filenames in the directory.
        """
        if os.path.exists(path) and os.path.isdir(path):
            return [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
        else:
            return []

    def copy_file(self, source, destination):
        """
        Copy a file from the source path to the destination path.

        Args:
            source (str): The path of the source file.
            destination (str): The path of the destination file.

        Returns:
            str: The path of the destination file.
        """
        shutil.copy(source, destination)
        return destination

    def execute_shell_command(self, command):
        """
        Execute a shell command and return the output.

        Args:
            command (str): The shell command to execute.

        Returns:
            str: The output of the command as a string.
        """
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""

    def get_system_info(self):
        """
        Get information about the operating system and system hardware.

        Returns:
            dict: A dictionary containing system information.
        """
        system_info = {
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "memory": os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024.0 ** 3),
            "disk_usage": shutil.disk_usage("/"),
        }
        return system_info

    def open_app(name):
        json = EMMA_GLOBALS.tools_da.json_loader(
            EMMA_GLOBALS.stcpath_app_dir, "app_dir", "dict"
        )
        for i in json.keys():
            if i == name:
                get = json.get(i)
                os.startfile(get)

    def path_mover():  # Need perfoance
        return
        diccionary = EMMA_GLOBALS.tools_da.json_loader(
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
