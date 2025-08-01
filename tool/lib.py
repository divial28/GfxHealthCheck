from .utils import local_path
import ctypes


class Lib(object):
    def __init__(self):
        self.lib = None

    def load(self):
        lib_path = local_path("bin/libGfxHealthCheck.so")
        self.lib = ctypes.CDLL(lib_path)
        self.lib.createGlxContext.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.createGlxContext.restype = ctypes.c_int
        self.lib.destroyGlxContext.argtypes = []
        self.lib.destroyGlxContext.restype = ctypes.c_int
        self.lib.gladLoadFunctions.argtypes = []
        self.lib.gladLoadFunctions.restype = ctypes.c_int
        self.lib.gladGetMajorVersion.argtypes = []
        self.lib.gladGetMajorVersion.restype = ctypes.c_int
        self.lib.gladGetMinorVersion.argtypes = []
        self.lib.gladGetMinorVersion.restype = ctypes.c_int

    def createGlxContext(self, w: int, h: int) -> int:
        return self.lib.createGlxContext(w, h)

    def destroyGlxContext(self) -> int:
        return self.lib.destroyGlxContext()

    def gladLoadFunctions(self) -> int:
        return self.lib.gladLoadFunctions()

    def gladGetVersion(self) -> tuple[int, int]:
        return self.lib.gladGetMajorVersion(), self.lib.gladGetMinorVersion()
