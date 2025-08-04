from .config import Config
from .lib import Lib
from .logging import TextColor
from .system_info import SystemInfo, ErrorContext
from .utils import run
from typing import List, Tuple, Union
import shutil
import sys
import time

lib = Lib()

PADDING = 50


def icon_ok() -> str:
    return TextColor.green("✔")


def icon_warn() -> str:
    return TextColor.yellow("⚠️")


def icon_fail() -> str:
    return TextColor.red("❌")


def print_started(label: str):
    sys.stdout.write(" ⏳ {} ".format(label))
    sys.stdout.flush()


def print_done(label: str, messages: List[Tuple[str, str]]):
    sys.stdout.write("\r" + " " * PADDING + "\r")
    sys.stdout.write(format_summary(label, messages, PADDING) + "\n")
    sys.stdout.flush()


def format_summary(label: str, messages: List[Tuple[str, str]], padding=PADDING):
    icon = icon_ok()
    for msg in messages:
        if msg[0] == "fail":
            icon = icon_fail()
            break
    line = " {}  {} ".format(icon, label)
    for msg in messages:
        icon = icon_fail() if msg[0] == "fail" else icon_warn()
        line += "\n     ↳ {} {}".format(icon, msg[1])
    return line


class Check(object):

    def __init__(
        self,
        label: str,
    ):
        self.label = label # type: str
        self.messages = [] # type: List[tuple[str, str]]

    def run(self, err_ctx: ErrorContext, info: SystemInfo, config: Config):
        print_started(self.label)
        self.__run__(err_ctx, info, config)
        print_done(self.label, self.messages)

    def is_ok(self) -> bool:
        return len(self.messages) == 0

    def fail(self, message: Union[str, bytes]):
        self.__add_message__("fail", message)

    def warn(self, message: Union[str, bytes]):
        self.__add_message__("warn", message)

    def __add_message__(self, type: str, message: Union[str, bytes]):
        if isinstance(message, bytes):
            message = message.decode("utf-8")
        self.messages.append((type, message))

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo, config: Config):
        raise NotImplementedError("Subclasses must implement __run__()")


class GPUCheck(Check):

    def __init__(self):
        super(GPUCheck, self).__init__("Checking GPU")

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo, config: Config):
        info.collect_gpu_info(err_ctx, config)

        if info.gpus_info is None:
            self.fail(err_ctx.gpu_info_parse_error or "No GPUs detected")
            return

        for gpu in info.gpus_info:
            if gpu.description is None or gpu.subsystem is None:
                self.fail("GPU info incomplete: description or subsystem missing")

            if gpu.kernel_module_in_use is None:
                self.fail(
                    "Driver info missing for GPU '{}'".format(
                        gpu.subsystem or "[unknown]"
                    )
                )

        is_nvidia = "NVIDIA" in gpu.description
        not_nvidia_module = gpu.kernel_module_in_use not in ("nvidia", "nouveau")
        if is_nvidia and not_nvidia_module:
            self.fail(
                "NVIDIA GPU '{}' uses unsupported driver '{}'".format(
                    gpu.subsystem or "[unknown]", gpu.kernel_module_in_use
                )
            )


class OpenGLInfoCheck(Check):
    def __init__(self):
        super(OpenGLInfoCheck, self).__init__("Checking OpenGL info")

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo, config: Config):
        if shutil.which("glxinfo") is None:
            self.fail(
                "glxinfo not found. Install it with 'sudo apt install mesa-utils'"
            )
            return

        info.collect_opengl_info(err_ctx, config)
        gl = info.opengl_info
        if gl is None:
            self.fail(err_ctx.opengl_info_parse_error or "Failed to parse OpenGL info")
            return

        if "llvmpipe" in gl.renderer.lower() or "softpipe" in gl.renderer.lower():
            self.warn("Software renderer detected: '{}'".format(gl.renderer))

        if gl.version is None:
            self.fail("Failed to get OpenGL version")

        major, minor = gl.version.major, gl.version.minor
        if major is None or minor is None:
            self.fail(
                err_ctx.opengl_version_parse_error or "Failed to parse OpenGL version"
            )
        elif major < 4 and minor < 3:
            self.fail(
                "OpenGL version too low: {}.{} ({})".format(
                    gl.version.major, gl.version.minor, gl.version.string
                )
            )


class OpenGLContextCheck(Check):
    def __init__(self):
        super(OpenGLContextCheck, self).__init__("Checking OpenGL context")

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo, config: Config):
        res = lib.createGlxContext(1, 1)
        if res.code != 0:
            self.fail(res.message)
            return

        res = lib.destroyGlxContext()
        if res.code != 0:
            self.fail(res.message)


class OpenGLFunctionsLoadCheck(Check):
    def __init__(self):
        super(OpenGLFunctionsLoadCheck, self).__init__(
            "Checking OpenGL functions loading"
        )

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo, config: Config):
        res = lib.createGlxContext(1, 1)
        if res.code != 0:
            self.fail(res.message)
            return

        res = lib.gladLoadFunctions()
        if res.code != 0:
            self.fail(res.message)

        major, minor = lib.gladGetVersion()
        res = lib.getOpenGLVersionString()
        if major < 4 and minor < 3:
            self.fail(
                "Loaded by glad OpenGL version too low: {}.{}".format(major, minor)
            )
        ver = info.opengl_info.version
        if major != ver.major or minor != ver.minor:
            self.warn(
                "Loaded by glad OpenGL version mismatch:"
                "\n\tglad:    {}.{}  '{}'"
                "\n\tglxinfo: {}.{}  '{}'".format(
                    major, minor, res.message.decode(), ver.major, ver.minor, ver.string
                )
            )

        res = lib.destroyGlxContext()
        if res.code != 0:
            self.fail(res.message)


class OpenGLFunctionsCallCheck(Check):
    def __init__(self):
        super(OpenGLFunctionsCallCheck, self).__init__(
            "Checking OpenGL basic function calls"
        )

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo, config: Config):
        res = lib.createGlxContext(1, 1)
        if res.code != 0:
            self.fail(res.message)
            return
        res = lib.gladLoadFunctions()
        if res.code != 0:
            self.fail(res.message)
            return
        res = lib.testBasicOpenGlFunctions()
        if res.code != 0:
            fails = res.message.decode().split("|")
            [self.fail(f) for f in fails]
        res = lib.destroyGlxContext()
        if res.code != 0:
            self.fail(res.message)


def run_checks(config: Config):
    TextColor.enable()
    info = SystemInfo()
    err_ctx = ErrorContext()
    info.collect_os_info(err_ctx, config)

    try:
        lib.load()
    except Exception as e:
        print(e)
        print("Build helper lib: `mkdir build && cd build && cmake .. && make -j8`")
        exit(1)

    GPUCheck().run(err_ctx, info, config)
    OpenGLInfoCheck().run(err_ctx, info, config)
    OpenGLContextCheck().run(err_ctx, info, config)
    OpenGLFunctionsLoadCheck().run(err_ctx, info, config)
    OpenGLFunctionsCallCheck().run(err_ctx, info, config)

    info.collect_journal_info(err_ctx, config)
    info.collect_packages_info(err_ctx, config)
