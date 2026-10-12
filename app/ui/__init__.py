"""FlowGuard desktop presentation layer.

The PyQt dependency is loaded lazily so foundation tests and headless CLI
users do not need a desktop Qt runtime just to import the package.
"""


def launch() -> int:
    from .main_window import launch as _launch

    return _launch()


def __getattr__(name: str):
    if name == "FlowGuardWindow":
        from .main_window import FlowGuardWindow

        return FlowGuardWindow
    raise AttributeError(name)


__all__ = ["FlowGuardWindow", "launch"]
