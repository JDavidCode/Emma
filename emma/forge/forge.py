import importlib


class Forge:
    def __init__(self):
        _g = importlib.import_module("emma.config.globals")
        self._builder = importlib.import_module(
            "emma.forge.builder.builder.Builder")
        self._repository = importlib.import_module(
            "emma.forge.handlers.repository_handler.RepositoryHandler")()
        self._download = importlib.import_module(
            "emma.forge.handlers.downloads_handler.DownloadsHandler")()
        self.sys_v_tm = _g.sys_v_tm
        self.sys_v_tm_cm = _g.sys_v_tm_cm
        self.sys_v_tm_qm = _g.sys_v_tm_qm
        self.tools_cs = _g.tools_cs
        self.tools_da = _g.tools_da
        self.tools_gs = _g.tools_gs

    def run(self, source, repository, package_name):
        print("Knowed repositories",
              self._repository.get_source_repositories(source))
        if not self._repository.verify_repository(repository):
            self._repository.add_repository(source, repository)
        else:
            print("The repository already exist, cannont install again")
            return

        key = self._download.download_package(repository, package_name)
        if key:
            self._builder(package_name)
