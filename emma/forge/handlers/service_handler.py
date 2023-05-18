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

    def add_service(self, service_data):
        service_list = self.data.setdefault(
            "Forge", {}).setdefault("services", [])
        service_list.append(service_data)
        self.save_data()
        print("Service added successfully.")

    def update_service(self, service_index, updated_service_data):
        service_list = self.data["Forge"]["services"]
        if 0 <= service_index < len(service_list):
            service_list[service_index] = updated_service_data
            self.save_data()
            print("Service updated successfully.")
        else:
            print("Invalid service index.")

    def remove_service(self, service_index):
        service_list = self.data["Forge"]["services"]
        if 0 <= service_index < len(service_list):
            del service_list[service_index]
            self.save_data()
            print("Service removed successfully.")
        else:
            print("Invalid service index.")

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
