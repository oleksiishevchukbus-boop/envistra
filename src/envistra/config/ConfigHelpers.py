"""
Configuration helper functions for validation and initialization.

These utilities reduce code duplication across config entity classes.
"""

def require_kwarg(kwargs, name, class_name):
    """Validate and return required kwarg, raising clear error if missing.

    Args:
        kwargs: Dictionary of keyword arguments
        name: Name of the required parameter
        class_name: Name of the class (for error message)

    Returns:
        The value of the required parameter

    Raises:
        ValueError: If the required parameter is not present
    """
    if name not in kwargs:
        raise ValueError(f"{name} is required for {class_name}")
    return kwargs[name]


def optional_kwarg(kwargs, name, default):
    """Return optional kwarg with default value.

    Args:
        kwargs: Dictionary of keyword arguments
        name: Name of the optional parameter
        default: Default value if parameter not present

    Returns:
        The parameter value if present, otherwise the default
    """
    return kwargs.get(name, default)
