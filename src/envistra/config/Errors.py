"""Configuration errors that name the file and field at fault.

The predecessor ran no validation on the load path: a misspelled key was simply
not found, so a default was used and the edit appeared to do nothing. Every
failure here says which file and which field, and suggests a correction when the
key is close to a known one.
"""
import difflib


class ConfigError(Exception):
    """A configuration file is missing, malformed, or inconsistent."""

    def __init__(self, path, message, field=None):
        self.path = str(path)
        self.field = field
        self.message = message
        location = self.path if field is None else f"{self.path}: {field}"
        super().__init__(f"{location}\n  {message}")


def unknown_key(path, key, known, context=""):
    """Reject an unrecognised key, suggesting the closest known one."""
    suggestion = difflib.get_close_matches(key, sorted(known), n=1, cutoff=0.6)
    hint = f" (did you mean {suggestion[0]!r}?)" if suggestion else ""
    where = f"{context}.{key}" if context else key
    return ConfigError(
        path,
        f"unknown key {key!r}{hint}\n"
        f"  known keys: {', '.join(sorted(known))}",
        field=where,
    )


def missing_key(path, key, context=""):
    where = f"{context}.{key}" if context else key
    return ConfigError(path, f"required key {key!r} is missing", field=where)


def bad_value(path, field, value, expected):
    return ConfigError(
        path,
        f"{value!r} is not valid here\n  expected: {expected}",
        field=field,
    )


def check_keys(path, data, required, optional=(), context=""):
    """Reject unknown keys and report missing required ones."""
    known = set(required) | set(optional)
    for key in data:
        if key not in known:
            raise unknown_key(path, key, known, context)
    for key in required:
        if key not in data:
            raise missing_key(path, key, context)
