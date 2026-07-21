import types
import sys


# Provide a minimal fake `vespa.application.Vespa` for tests so the package
# can be imported without installing the real Vespa Python client.
vespa = types.ModuleType("vespa")
application = types.ModuleType("vespa.application")


class Vespa:
    def __init__(self, *args, **kwargs):
        pass


application.Vespa = Vespa
vespa.application = application

sys.modules["vespa"] = vespa
sys.modules["vespa.application"] = application
