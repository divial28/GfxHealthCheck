from .utils import local_path
import ctypes


class Lib(object):

    class Result(ctypes.Structure):
        _fields_ = [
            ("code", ctypes.c_int),
            ("message", ctypes.c_char_p),
        ]

    def __init__(self):
        self.lib = None

    def load(self):
        lib_path = local_path("bin/libGfxHealthCheck.so")
        self.lib = ctypes.CDLL(lib_path)
        self.lib.createGlxContext.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.createGlxContext.restype = Lib.Result
        self.lib.destroyGlxContext.argtypes = []
        self.lib.destroyGlxContext.restype = Lib.Result
        self.lib.gladLoadFunctions.argtypes = []
        self.lib.gladLoadFunctions.restype = Lib.Result
        self.lib.gladGetMajorVersion.argtypes = []
        self.lib.gladGetMajorVersion.restype = ctypes.c_int
        self.lib.gladGetMinorVersion.argtypes = []
        self.lib.gladGetMinorVersion.restype = ctypes.c_int
        self.lib.testBasicOpenGlFunctions.argtypes = []
        self.lib.testBasicOpenGlFunctions.restype = Lib.Result

    def createGlxContext(self, w: int, h: int) -> Result:
        return self.lib.createGlxContext(w, h)

    def destroyGlxContext(self) -> int:
        return self.lib.destroyGlxContext()

    def gladLoadFunctions(self) -> int:
        return self.lib.gladLoadFunctions()

    def gladGetVersion(self) -> tuple[int, int]:
        return self.lib.gladGetMajorVersion(), self.lib.gladGetMinorVersion()

    def testBasicOpenGlFunctions(self) -> Result:
        return self.lib.testBasicOpenGlFunctions()
