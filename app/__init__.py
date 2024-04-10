import os
import pkg_resources
import subprocess


class Run:
    """
    Esta clase se utiliza para inicializar la aplicación y comenzar los servicios.

    Args:
        name (str): El nombre de esta instancia.
        queue_name (str): El nombre de la cola.
        queue_handler: Un objeto responsable de manejar la cola.
        thread_manager: Un objeto responsable de gestionar los hilos.
        system_events: Un objeto para gestionar eventos del sistema.
        tools (list, opcional): Herramientas adicionales para usar. Por defecto, una lista vacía.
    """

    def establish_connections(self):
        """
        Establece las conexiones necesarias para la aplicación. #actualizar requisitos etc
        """
        self.required_packages = [
            'pandas',
            'numpy',
            'matplotlib',
            'youtube-dl',
            'sqlalchemy',
            'pymysql',
            'imutils',
            'pyyaml',
            'img2pdf',
            'psutil',
            'openai',
            'flask-socketio',
            'flask',
            'sqlalchemy',
            'geopy',
            'selenium',
            'chromedriver_autoinstaller',
            'panda3d',
            'mplfinance',
            'pillow',
            'pytelegrambotapi',
            'langchain',
            'pypdf2',
            'faiss-cpu',
            'google-generativeai',
            'langchain_google_genai'
        ]

    def set_environ_variables(self):
        """
        Establece variables de entorno basadas en la configuración del usuario.
        """
        pass

    def verify_paths(self):
        """
        Verify and create directory paths if they don't exist.

        Returns:
            str: Confirmation message.
        """
        DirsStructure = [
            "./app/common/.temp",
            "./app/services/external",
        ]

        for path in DirsStructure:
            if not os.path.exists(path):
                os.makedirs(path)

        return "All Directories have been verified correctly"

    def check_dependencies(self):
        """
        Comprueba y maneja las dependencias de la aplicación.
        """
        missing_packages = self.get_missing_packages()

        if missing_packages:
            print("Faltan dependencias. Instalando...", " : ", missing_packages)

            self.install_dependencies(missing_packages)
            print("Dependencias instaladas.")
        else:
            print("Todas las dependencias están satisfechas.")

    def store_installed_libraries_to_env(self):
        """
        Almacena las bibliotecas instaladas en una variable de entorno.
        """
        installed_packages = self.get_installed_packages()
        libraries_str = ",".join(installed_packages)
        os.environ[self.env_var_name] = libraries_str

    def get_installed_packages(self):
        """
        Obtiene una lista de paquetes instalados.
        """
        installed_packages = [pkg.project_name.lower()
                              for pkg in pkg_resources.working_set]
        return installed_packages

    def get_missing_packages(self):
        """
        Obtiene una lista de paquetes faltantes.
        """
        missing_packages = []
        for package in self.required_packages:
            if not self.is_package_installed(package):
                missing_packages.append(package)

        return missing_packages

    def install_dependencies(self, packages):
        """
        Instala paquetes faltantes usando pip.
        """
        try:
            # Verifica la versión de pip y actualiza si es necesario
            subprocess.run('pip install --upgrade pip', shell=True, check=True)

            for package in packages:
                # Verifica si el paquete ya está instalado
                if not self.is_package_installed(package):
                    print(f"Instalando {package}...")
                    subprocess.run(
                        f'pip install {package}', shell=True, check=True)
                else:
                    print(f"{package} ya está instalado.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

    def is_package_installed(self, package):
        """
        Verifica si un paquete está instalado.
        """
        try:
            subprocess.run(f'pip show {package}', shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def perform_health_checks(self):
        """
        Realiza comprobaciones de salud para la aplicación.
        """
        pass

    def run(self):
        """
        Ejecuta el proceso de inicio de la aplicación.
        """
        package_list = [
            {
                "repository": "https://github.com/ItsMaper/Emma-Trading_Bots/releases/download/v1.0.0/trading_bots.zip",
                "package_name": "trading_bots",
            }
        ]
        self.establish_connections()
        self.set_environ_variables()
        self.verify_paths()
        self.check_dependencies()
        self.perform_health_checks()
