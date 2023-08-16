class ServiceHandler:
    def __init__(self, tools=[]):
        self.tools_cs, self.tools_da = tools
        self.file_path = "./emma/config/forge_config.yml"
        self.data = {}
        self.load_data()

    def load_data(self):
        self.data = self.tools_da.yaml_loader(self.file_path)

    def save_data(self):
        self.tools_da.yaml_saver(self.file_path, self.data)

    def add_service(self, service_data, is_forge_package=True):
        forge_data = self.data.setdefault("Forge", {})
        service_list = forge_data.setdefault("services", [])
        service_list.append(service_data)

        if not is_forge_package:
            self.file_path = "emma/config/server_config.yml"
            self.load_data()
        self.save_data()

    def update_service(self, package_name, updated_service_data):
        service_list = self.data["Forge"]["services"]
        for service in service_list:
            if "package_name" in service and service["package_name"] == package_name:
                service_list[package_name] = updated_service_data
                self.save_data()
                print("Service updated successfully.")
                return
            else:
                print(f"Service not found. {package_name}")

    def remove_service(self, package_name):
        service_list = self.data["Forge"]["services"]
        for service in service_list:
            if "package_name" in service and service["package_name"] == package_name:
                del service_list[package_name]
                self.save_data()
                print(f"Service {package_name} removed successfully.")
                return
            else:
                print(f"Service not found. {package_name}")

    def add_queue(self, queue_data):
        queue_list = self.data.setdefault("Forge", {}).setdefault("queues", [])
        queue_list.append(queue_data)
        self.save_data()
        print("Queue added successfully.")

    def verify_service(self, package_name):
        service_list = self.data["Forge"]["services"]
        for service in service_list:
            if "package_name" in service and service["package_name"] == package_name:
                return True
        return False

    def get_service(self, package_name):
        service_list = self.data["Forge"]["services"]
        for service in service_list:
            if "package_name" in service and service["package_name"] == package_name:
                return service
        print(f"Service with package name '{package_name}' does not exist.")
