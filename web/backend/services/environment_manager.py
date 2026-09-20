"""Read and write `config/environment.json`.

GET reads the **file**, never the config classes. Those classes now hold no
values of their own and raise `ConfigNotLoadedError` when read before the
environment has been loaded — which, with a lazily-constructed service, is
exactly the first request.

Writes go through `envistra.config.Writer`, which validates before touching
disk, so a rejected document leaves both the file and the live classes as they
were. The predecessor applied first and rolled back on failure.
"""
from envistra.config import Loader, Writer


class EnvironmentManager:
    def _path(self):
        return Loader.config_dir() / "environment.json"

    def get(self):
        """The regime as stored on disk."""
        return Loader._read(self._path())

    def update(self, changes):
        """Merge whole top-level blocks over the stored document.

        Block-level rather than field-level, matching the predecessor's PUT — but
        note the loader now requires every key within a block, so a partial block
        is rejected rather than silently keeping stale values.
        """
        document = {**self.get(), **changes}
        Writer.save_environment(document, self._path())
        Loader.load_environment(self._path())  # apply, now that it is known good
        return self.get()

    def reload(self):
        """Re-read the file and apply it to the live config classes."""
        return Loader.load_environment(self._path())


_manager = EnvironmentManager()


def get_environment_manager() -> EnvironmentManager:
    return _manager
