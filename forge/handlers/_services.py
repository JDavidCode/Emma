import logging

class ServiceHandler:
    CONFIG_FILE_PATH = "forge/config/config.yml"
    
    def __init__(self, tools=[]):
        self.tools_da, self.tools_cs = tools
        self.data = {}
        self.load_data()

    def load_data(self):
        try:
            self.data = self.tools_da.yaml_loader(self.CONFIG_FILE_PATH)
        except Exception as e:
            logging.error(f"Error loading data: {e}")

    def save_data(self):
        try:
            self.tools_da.yaml_saver(self.CONFIG_FILE_PATH, self.data)
        except Exception as e:
            logging.error(f"Error saving data: {e}")

    def add_service(self, service_data, is_forge_package=True):
        try:
            forge_data = self.data.setdefault("Forge", {})
            service_list = forge_data.setdefault("services", [])
            service_list.append(service_data)

            if not is_forge_package:
                self.CONFIG_FILE_PATH = "./app/config/server_config.yml"
                self.load_data()
            self.save_data()
            logging.info("Service added successfully.")
        except Exception as e:
            logging.error(f"Error adding service: {e}")

    def update_service(self, package_name, updated_service_data):
        try:
            service_list = self.data["Forge"]["services"]
            for service in service_list:
                if "package_name" in service and service["package_name"] == package_name:
                    service_list[package_name] = updated_service_data
                    self.save_data()
                    logging.info("Service updated successfully.")
                    return
            logging.warning(f"Service not found: {package_name}")
        except Exception as e:
            logging.error(f"Error updating service: {e}")

    def remove_service(self, package_name):
        try:
            service_list = self.data["Forge"]["services"]
            for service in service_list:
                if "package_name" in service and service["package_name"] == package_name:
                    service_list.remove(service)
                    self.save_data()
                    logging.info(f"Service {package_name} removed successfully.")
                    return
            logging.warning(f"Service not found: {package_name}")
        except Exception as e:
            logging.error(f"Error removing service: {e}")

    def add_queue(self, queue_data):
        try:
            queue_list = self.data.setdefault("Forge", {}).setdefault("queues", [])
            queue_list.append(queue_data)
            self.save_data()
            logging.info("Queue added successfully.")
        except Exception as e:
            logging.error(f"Error adding queue: {e}")

    def verify_service(self, package_name):
        try:
            service_list = self.data["Forge"]["services"]
            for service in service_list:
                if "package_name" in service and service["package_name"] == package_name:
                    return True
            return False
        except Exception as e:
            logging.error(f"Error verifying service: {e}")
            return False

    def get_service(self, package_name):
        try:
            service_list = self.data["Forge"]["services"]
            for service in service_list:
                if "package_name" in service and service["package_name"] == package_name:
                    return service
            logging.warning(f"Service not found: {package_name}")
        except Exception as e:
            logging.error(f"Error retrieving service: {e}")
        return None

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    pass  # Add your application logic here
