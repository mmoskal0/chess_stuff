from importlib import import_module
from pkgutil import walk_packages

from .base import AVAILABLE_COMMANDS

# Recursively import all commands to register them in AVAILABLE_COMMANDS
pkgs = (
    "commands",
    "commands.browser",
    "commands.websockets",
)
for pkg in pkgs:
    path = import_module(pkg).__path__
    for loader, name, is_pkg in walk_packages(path):
        import_module(".".join([pkg, name]))
