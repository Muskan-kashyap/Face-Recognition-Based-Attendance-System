import os

# Prevent pytest from auto-loading external plugins (notably anyio/async plugins)
# which are currently breaking test startup in this environment.
os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
