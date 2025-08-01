from typing import List
from .system_info import SystemInfo, ErrorContext
from .logging import TextColor
from pathlib import Path
import sys
import enum
import shutil
import ctypes

PADDING = 45


def icon_ok():
    return TextColor.green("✔")


def icon_warn():
    return TextColor.yellow("⚠")


def icon_fail():
    return TextColor.red("❌")


def print_started(label: str):
    sys.stdout.write(label + "...")
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

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo):
        raise NotImplementedError("Subclasses must implement __run__()")


class GPUCheck(Check):

    def __init__(self):
        super(GPUCheck, self).__init__("Cheking GPU")

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo):
        info.collect_gpu_info(err_ctx)

        if info.gpus_info is None:
            self.errors.append("No GPUs detected")
            return

        for gpu in info.gpus_info:
            if gpu.description is None or gpu.subsystem is None:
                self.errors.append(
                    "GPU info incomplete: description or subsystem missing"
                )


class DriverCheck(Check):

    def __init__(self):
        super(DriverCheck, self).__init__("Cheking driver")

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo):
        if info.gpus_info is None:
            self.errors.append(err_ctx.gpu_info_parse_error or "No GPUs detected")
            return

        for gpu in info.gpus_info:
            if gpu.description is None or gpu.kernel_module_in_use is None:
                self.errors.append(
                    "Driver info missing for GPU '{}'".format(
                        gpu.subsystem or "[unknown]"
                    )
                )

            is_nvidia = "NVIDIA" in gpu.description
            not_nvidia_module = gpu.kernel_module_in_use not in ("nvidia", "nouveau")
            if is_nvidia and not_nvidia_module:
                self.errors.append(
                    "NVIDIA GPU '{}' uses unsupported driver '{}'".format(
                        gpu.subsystem or "[unknown]", gpu.kernel_module_in_use
                    )
                )


class GlxInfoCheck(Check):
    def __init__(self):
        super(GlxInfoCheck, self).__init__("Checking OpenGL info")

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo):
        if shutil.which("glxinfo") is None:
            self.errors.append(
                "glxinfo not found. Install it with 'sudo apt install mesa-utils'"
            )
            return

        info.collect_glx_info(err_ctx)
        gl = info.opengl_info
        if gl is None or gl.renderer is None:
            self.errors.append("OpenGL renderer info not available")

        if "llvmpipe" in gl.renderer.lower() or "softpipe" in gl.renderer.lower():
            self.warnings.append("Software renderer detected: '{}'".format(gl.renderer))

        if gl.version is None:
            self.errors.append("Failed to get OpenGL version")

        if (
            gl.version.major is None
            or gl.version.minor is None
            or gl.version.major < 4
            or gl.version.minor < 3
        ):
            self.errors.append(
                "OpenGL version too low: {}.{} ({})".format(
                    gl.version.major, gl.version.minor, gl.version.string
                )
            )


class OpenGLContextCheck(Check):
    def __init__(self):
        super(OpenGLContextCheck, self).__init__("Checking OpenGL context")

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo):
        script_dir = Path(__file__).parent.resolve()
        lib_path = script_dir.joinpath("../bin/libGfxHealthCheck.so").absolute()
        lib = ctypes.CDLL(lib_path)
        lib.checkContext.argtypes = []
        lib.checkContext.restype = ctypes.c_int
        res = lib.checkContext()
        if res != 0:
            self.errors.append("Failed to create opengl context")


class OpenGLFunctionsLoad(Check):
    def __init__(self):
        super(OpenGLFunctionsLoad, self).__init__("Checking OpenGL functions loading")

    def __run__(self, err_ctx: ErrorContext, info: SystemInfo): ...


def run_checks():
    TextColor.enable()
    info = SystemInfo()
    err_ctx = ErrorContext()
    info.collect_os_info(err_ctx)
    GPUCheck().run(err_ctx, info)
    DriverCheck().run(err_ctx, info)
    GlxInfoCheck().run(err_ctx, info)
    OpenGLContextCheck().run(err_ctx, info)
    OpenGLFunctionsLoad().run(err_ctx, info)
