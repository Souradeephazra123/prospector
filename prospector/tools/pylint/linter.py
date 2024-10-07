from pathlib import Path

from packaging import version as packaging_version
from pylint import version as pylint_version
from pylint.config.config_initialization import _config_initialization
from pylint.lint import PyLinter


class UnrecognizedOptions(Exception):
    """Raised when an unrecognized option is found in the Pylint configuration."""

    pass


class ProspectorLinter(PyLinter):
    def __init__(self, found_files, *args, **kwargs):
        self._files = found_files
        # set up the standard PyLint linter
        PyLinter.__init__(self, *args, **kwargs)

    # Largely inspired by https://github.com/pylint-dev/pylint/blob/main/pylint/config/config_initialization.py#L26
    def config_from_file(self, config_file=None):
        """Initialize the configuration from a file."""
        _config_initialization(self, [], config_file=config_file)
        return True

    def _expand_files(self, modules):
        expanded = super()._expand_files(modules)
        filtered = {}
        # PyLinter._expand_files returns dict since 2.15.7.
        if packaging_version.parse(pylint_version) > packaging_version.parse("2.15.6"):
            for module in expanded:
                if not self._files.is_excluded(Path(module)):
                    filtered[module] = expanded[module]
            return filtered
        else:
            for module in expanded:
                # need to de-duplicate, as pylint also walks directories given to it, so it will find
                # files that prospector has already provided and end up checking it more than once
                if not self._files.is_excluded(Path(module["path"])):
                    # if the key exists, just overwrite it with the same value, so we don't need an extra if statement
                    filtered[module["path"]] = module
            return filtered.values()
