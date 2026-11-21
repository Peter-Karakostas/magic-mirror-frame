"""Magic Mirror - frame_test_pair: builds ONLY one short joint pair
(TEST_pole_piece + TEST_hole_piece) for a fit test before printing the
frame. It runs ../frame/frame.py in TEST mode, so there is one copy of
the frame code. Run setup_parameters first, in a new empty design.
"""
import adsk.core, traceback, os, importlib.util


def run(context):
    ui = None
    try:
        ui = adsk.core.Application.get().userInterface
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(os.path.dirname(here), "frame", "frame.py")
        if not os.path.isfile(path):
            ui.messageBox("frame_test_pair: cannot find\n" + path +
                          "\nKeep the frame folder next to this one.")
            return
        spec = importlib.util.spec_from_file_location("mirror_frame_test", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.MODE = "TEST"
        mod.run(context)
    except Exception:
        if ui: ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
