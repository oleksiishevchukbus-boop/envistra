"""Strategy CRUD over `config/strategies/*.json`, one file per strategy.

The files are already in the shape the API exposes, so this reads and writes
them directly rather than round-tripping through a serializer. Every write goes
through `envistra.config.Writer`, which validates with the same parser that will
read the file back and writes atomically — a rejected write leaves the previous
file intact, which matters because invalid config stops the app from starting.

Strategies are addressed by **display name**. Storage is keyed by filename stem,
so this maps one to the other; `Loader` enforces that names are unique.
"""
from envistra.config import Loader, Writer
from envistra.config.Errors import ConfigError


class StrategyManager:
    """Reads the strategy directory on demand; holds no cache.

    The predecessor cached, which meant the UI and the simulation could disagree
    until something called reload. The directory is four small files.
    """

    def _directory(self):
        return Loader.config_dir() / "strategies"

    def _documents(self):
        """{id: raw document} straight from disk."""
        return {path.stem: Loader._read(path)
                for path in sorted(self._directory().glob("*.json"))}

    def _id_for(self, name):
        for strategy_id, doc in self._documents().items():
            if doc.get("name") == name:
                return strategy_id
        return None

    # ------------------------------------------------------------------ read

    def list(self):
        """Every strategy, with a short summary for list display."""
        out = []
        for strategy_id, doc in self._documents().items():
            ratios = doc["estimators"]["investment"]["investmentRatios"]
            out.append({
                "id": strategy_id,
                "name": doc["name"],
                "description": doc.get("description", ""),
                "color": doc.get("color", "#888888"),
                "summary": {
                    "investment_split": (f"{int(ratios.get('finInvestment', 0) * 100)}% Financial"
                                         f" / {int(ratios.get('ecoInvestment', 0) * 100)}% Ecological"),
                    "pollution_estimator": doc["estimators"]["pollution"]["approach"],
                    "buy_price_approach": doc["calculators"]["quota_to_buy_price"]["approach"],
                    "quota_reserve": doc["calculators"]["quota_to_buy_amount"]["quotaReserve"],
                },
            })
        return out

    def get(self, name):
        strategy_id = self._id_for(name)
        if strategy_id is None:
            return None
        doc = self._documents()[strategy_id]
        return {"id": strategy_id, **doc}

    def used_by(self, name):
        """Companies referencing this strategy — what blocks a delete."""
        strategy_id = self._id_for(name)
        if strategy_id is None:
            return []
        strategies = Loader.load_strategies(self._directory())
        return [c.name for c in Loader.load_companies(strategies)
                if c.strategyId == strategy_id]

    # ----------------------------------------------------------------- write

    def create(self, document):
        name = document.get("name")
        if self._id_for(name) is not None:
            raise ConfigError(message=f"a strategy named {name!r} already exists")

        strategy_id = Writer.slugify(name)
        if strategy_id in self._documents():
            raise ConfigError(message=f"{strategy_id}.json already exists; "
                                      f"choose a name that yields a different filename")
        Writer.save_strategy(strategy_id, document, self._directory())
        return self.get(name)

    def update(self, name, changes):
        """Merge changes into the stored document.

        Renaming edits the `name` field and leaves the file where it is —
        companies reference the filename stem, so moving it would orphan them.
        """
        strategy_id = self._id_for(name)
        if strategy_id is None:
            return None

        document = {**self._documents()[strategy_id], **changes}
        document.pop("id", None)
        Writer.save_strategy(strategy_id, document, self._directory())
        return self.get(document["name"])

    def delete(self, name):
        strategy_id = self._id_for(name)
        if strategy_id is None:
            return False
        # Writer refuses while any company still points at it.
        Writer.delete_strategy(strategy_id, self._directory())
        return True

    def clone(self, name, new_name):
        source = self.get(name)
        if source is None:
            return None
        document = {k: v for k, v in source.items() if k != "id"}
        document["name"] = new_name
        return self.create(document)

    def reload(self):
        """Re-read the directory and apply it — the files are the source."""
        return Loader.load_strategies(self._directory())


_manager = StrategyManager()


def get_strategy_manager() -> StrategyManager:
    return _manager
