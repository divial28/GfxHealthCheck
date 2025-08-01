from typing import List
from .system_info import SystemInfo, ErrorContext
from .logging import TextColor
from .lib import Lib

import sys
import shutil


lib = Lib()

PADDING = 45


def icon_ok():
    return TextColor.green("✔")


def icon_warn():
    return TextColor.yellow("⚠️")


def icon_fail():
    return TextColor.red("❌")


def print_started(label: str):
    sys.stdout.write(label + " ")
    sys.stdout.flush()


def print_done(label: str, errors: List[str], warnings: List[str]):
    sys.stdout.write("\r" + " " * PADDING + "\r")
    sys.stdout.write(format_summary(label, errors, warnings) + "\n")
    sys.stdout.flush()


def format_summary(label: str, errors: List[str], warnings: List[str], padding=PADDING):
    icon = icon_ok()
    if len(errors) > 0:
        icon = icon_fail()
    elif len(warnings) > 0:
        icon = icon_warn()
    line = label.ljust(padding, "·") + icon
    for err in errors:
        line += "\n   ↳ {} {}".format(icon_fail(), err)
    for warn in warnings:
        line += "\n   ↳ {} {}".format(icon_warn(), warn)
    return line


class Check(object):

    def __init__(
        self,
        label: str,
    ):
        self.label: str = label
        self.warnings: List[str] = []
        self.errors: List[str] = []

    def run(self, err_ctx: ErrorContext, info: SystemInfo):
        print_started(self.label)
        self.__run__(err_ctx, info)
        print_done(self.label, self.errors, self.warnings)

    def is_ok(self):
        return len(self.errors) == 0 and len(self.warnings) == 0

    def fail(self, message: str):
        self.errors.append(message)

    def warn(self, message: str):
        self.warnings.append(message)

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo):
        raise NotImplementedError("Subclasses must implement __run__()")


class GPUCheck(Check):

    def __init__(self):
        super(GPUCheck, self).__init__("Cheking GPU")

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo):
        info.collect_gpu_info(err_ctx)

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

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo):
        if shutil.which("glxinfo") is None:
            self.fail(
                "glxinfo not found. Install it with 'sudo apt install mesa-utils'"
            )
            return

        info.collect_opengl_info(err_ctx)
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

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo):
        res = lib.createGlxContext(1, 1)
        if res == 1:
            self.fail("GLX failed to open X display")
            return
        elif res == 2:
            self.fail("GLX couldn't find appropriate visual")
            return
        elif res == 3:
            self.fail("GLX dailed to create OpenGL context")
            return

        if lib.destroyGlxContext() != 0:
            self.fail("GLX failed to destroy OpenGL context")


class OpenGLFunctionsLoad(Check):
    def __init__(self):
        super(OpenGLFunctionsLoad, self).__init__("Checking OpenGL functions loading")

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo):
        if lib.createGlxContext(1, 1) != 0:
            self.fail("GLX failed to create OpenGL context")
            return

        if lib.gladLoadFunctions() == 0:  # glad returns true/false
            self.fail("GLX failed to load OpenGL functions")

        major, minor = lib.gladGetVersion()
        if major < 4 and minor < 3:
            self.fail(
                "Loaded by glad OpenGL version too low: {}.{}".format(major, minor)
            )
        ver = info.opengl_info.version
        if major != ver.major or minor != ver.minor:
            self.warn(
                "Loaded by glad OpenGL version mismatch:\n\tglad:    {}.{}\n\tglxinfo: {}.{}".format(
                    major, minor, ver.major, ver.minor
                )
            )

        if lib.destroyGlxContext() != 0:
            self.fail("Failed to destroy OpenGL context")


def run_checks():
    TextColor.enable()
    info = SystemInfo()
    err_ctx = ErrorContext()
    info.collect_os_info(err_ctx)

    try:
        lib.load()
    except Exception as e:
        print(e)
        print("Build helper lib: `mkdir build && cd build && cmake .. && make -j8`")
        exit(1)

    GPUCheck().run(err_ctx, info)
    OpenGLInfoCheck().run(err_ctx, info)
    OpenGLContextCheck().run(err_ctx, info)
    OpenGLFunctionsLoad().run(err_ctx, info)
