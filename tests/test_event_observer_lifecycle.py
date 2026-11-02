import importlib.util
import sys
import types
from pathlib import Path


def load_observer(monkeypatch):
    calls = []
    class Console:
        @staticmethod
        def PrintMessage(message):
            calls.append(("log", message))

    class Selection:
        @staticmethod
        def addObserver(observer):
            calls.append(("selection_add", observer))

        @staticmethod
        def removeObserver(observer):
            calls.append(("selection_remove", observer))

    class MainWindow:
        def installEventFilter(self, observer):
            calls.append(("filter_add", observer))

        def removeEventFilter(self, observer):
            calls.append(("filter_remove", observer))

    window = MainWindow()
    freecad = types.ModuleType("FreeCAD")
    freecad.Console = Console()
    freecad.addDocumentObserver = lambda observer: calls.append(("document_add", observer))
    freecad.removeDocumentObserver = lambda observer: calls.append(("document_remove", observer))

    gui = types.ModuleType("FreeCADGui")
    gui.Selection = Selection()
    gui.getMainWindow = lambda: window

    qtcore = types.SimpleNamespace(QObject=object, QEvent=types.SimpleNamespace(
        HoverEnter=1, MouseButtonPress=2
    ))
    pyside = types.ModuleType("PySide")
    pyside.QtCore = qtcore

    monkeypatch.setitem(sys.modules, "FreeCAD", freecad)
    monkeypatch.setitem(sys.modules, "FreeCADGui", gui)
    monkeypatch.setitem(sys.modules, "PySide", pyside)

    path = Path(__file__).parents[1] / "AICopilot" / "event_observer.py"
    spec = importlib.util.spec_from_file_location("cadpilot_test_event_observer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.FreeCADEventObserver, calls


def test_start_is_idempotent_and_stop_detaches_all_observers(monkeypatch):
    observer_type, calls = load_observer(monkeypatch)
    observer = observer_type()

    observer.start()
    observer.start()

    assert observer._started is True
    assert [name for name, _ in calls].count("selection_add") == 1
    assert [name for name, _ in calls].count("document_add") == 1
    assert [name for name, _ in calls].count("filter_add") == 1

    observer.stop()
    observer.stop()

    assert observer._started is False
    assert observer._main_window is None
    assert [name for name, _ in calls].count("selection_remove") == 1
    assert [name for name, _ in calls].count("document_remove") == 1
    assert [name for name, _ in calls].count("filter_remove") == 1


def test_stop_before_start_is_safe(monkeypatch):
    observer_type, calls = load_observer(monkeypatch)
    observer = observer_type()

    observer.stop()

    assert observer._started is False
    assert not any(name.endswith("_remove") for name, _ in calls)
