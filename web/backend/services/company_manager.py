"""Company CRUD over `config/companies/*.json` — one file per agent.

New in this backend: the predecessor had no agent API at all, because the roster
was a hardcoded Python list. The number of files is now the number of agents, so
creating and deleting here changes the simulation.

Companies are addressed by their `name`, which is also the agent label in
results and plot legends. `Loader` enforces that names are unique.
"""
from envistra.config import Loader, Writer
from envistra.config.Errors import ConfigError


class CompanyManager:
    def _directory(self):
        return Loader.config_dir() / "companies"

    def _documents(self):
        return {path.stem: Loader._read(path)
                for path in sorted(self._directory().glob("*.json"))}

    def _id_for(self, name):
        for company_id, doc in self._documents().items():
            if doc.get("name") == name:
                return company_id
        return None

    def _strategies(self):
        return Loader.load_strategies()

    # ------------------------------------------------------------------ read

    def list(self):
        """Every company, with the colour it will actually be drawn in.

        A company that declares no colour is assigned one at load time, so the
        stored document and the effective colour differ; the UI needs the latter.
        """
        effective = {c.configId: c for c in Loader.load_companies(self._strategies())}
        out = []
        for company_id, doc in self._documents().items():
            loaded = effective.get(company_id)
            out.append({
                "id": company_id,
                "name": doc["name"],
                "dataSource": doc["dataSource"],
                "strategy": doc["strategy"],
                "strategyName": loaded.strategyName if loaded else None,
                "enabled": doc.get("enabled", True),
                "plot": doc.get("plot", True),
                "color": doc.get("color"),
                "effectiveColor": loaded.color if loaded else None,
                "parameters": doc["parameters"],
            })
        return out

    def get(self, name):
        company_id = self._id_for(name)
        if company_id is None:
            return None
        return next(c for c in self.list() if c["id"] == company_id)

    # ----------------------------------------------------------------- write

    def create(self, document):
        name = document.get("name")
        if self._id_for(name) is not None:
            raise ConfigError(message=f"a company named {name!r} already exists")

        company_id = Writer.slugify(name)
        if company_id in self._documents():
            raise ConfigError(message=f"{company_id}.json already exists; "
                                      f"choose a name that yields a different filename")
        Writer.save_company(company_id, document, self._directory(), self._strategies())
        return self.get(name)

    def update(self, name, changes):
        company_id = self._id_for(name)
        if company_id is None:
            return None

        document = {**self._documents()[company_id], **changes}
        for derived in ("id", "strategyName", "effectiveColor"):
            document.pop(derived, None)
        if document.get("color") is None:
            document.pop("color", None)

        Writer.save_company(company_id, document, self._directory(), self._strategies())
        return self.get(document["name"])

    def delete(self, name):
        company_id = self._id_for(name)
        if company_id is None:
            return False
        # Writer refuses to remove the last enabled company.
        Writer.delete_company(company_id, self._directory())
        return True

    def reload(self):
        return Loader.load_companies(self._strategies())


_manager = CompanyManager()


def get_company_manager() -> CompanyManager:
    return _manager
