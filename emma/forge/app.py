import importlib


class Forge:
    def __init__(self, tools=[]):
        self.tools_cs, self.tools_da = tools
        self._builder = importlib.import_module(
            "emma.forge.builder.builder")

        _repository = importlib.import_module(
            "emma.forge.handlers.repository_handler")
        self._repository = _repository.RepositoryHandler(tools)
        _download = importlib.import_module(
            "emma.forge.handlers.downloads_handler")
        self._download = _download.DownloadsHandler(tools)

    def run(self, package_list):
        for package in package_list:
            source = package.get('source')
            repository = package.get('repository')
            package_name = package.get('package_name')
            if not all([source, repository, package_name]):
                print("Missing required parameters")
                continue
            self._builder = self._builder.Builder(
                package_name, [self.tools_cs, self.tools_da])

            print(f"Known {source} source repositories:",
                  self._repository.get_source_repositories(source))
            if not self._repository.verify_repository(repository):
                self._repository.add_repository(source, repository)
            else:
                print("The repository already exists, cannot install again")
                continue

            key = self._download.download_package(repository, package_name)
            if key:
                self._builder.run()
