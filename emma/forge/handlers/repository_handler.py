from emma.config.globals import tools_da


class RepositoryHandler:
    def __init__(self):
        self.file_path = "./emma/forge/config/config.yml"
        self.sources = {}

    def load_data(self):
        self.sources = tools_da.yaml_loader(
            self.file_path, "repositories")

    def save_data(self):
        data = {"version": "1.0", "repositories": self.sources}
        tools_da.yaml_saver(self.file_path, data)

    def add_repository(self, source, repository):
        if source in self.sources:
            self.sources[source].extend(repository)
        else:
            print("the source is unknowed, indexing...")
            self.sources[source] = repository
        self.save_data()

    def get_source_repositories(self, source):
        if source in self.sources:
            return self.sources[source]
        return []

    def verify_repository(self, repository_name):
        for key in self.sources:
            if repository_name in self.sources[key]:
                return True
            return False

    def verify_source(self, source):
        if source in self.sources:
            return True
        return False

    def remove_source(self, source):
        if source in self.sources:
            del self.sources[source]
            self.save_data()
            return True
        return False
