from .system_info import SystemInfo
from .logging import TextColor
import sys
import enum

PADDING = 40


class CheckStatus(enum.Enum):
    PENDING = 0
    OK = 1
    WARNING = 2
    FAIL = 3


def icon(status: CheckStatus):
    if status == CheckStatus.OK:
        return TextColor.green("✔")
    if status == CheckStatus.WARNING:
        return TextColor.yellow("⚠")
    if status == CheckStatus.FAIL:
        return TextColor.red("❌")
    return ""


class Check(object):

    def __init__(
        self,
        label: str = "",
        status: CheckStatus = CheckStatus.PENDING,
        message: str = None,
    ):
        self.label: str = label
        self.status: CheckStatus = status
        self.message: str = message or ""

    def run(self, info: SystemInfo):
        self.__pre_run__()
        self.__run__(info)
        self.__post_run__()

    def is_ok(self):
        return self.status == CheckStatus.OK

    def format_summary(self, padding=PADDING):
        line = self.label.ljust(padding) + icon(self.status)
        if self.status != CheckStatus.OK and self.message:
            line += "\n   ↳ " + self.message
        return line

    def __pre_run__(self):
        sys.stdout.write(self.label + "...")
        sys.stdout.flush()

    def __run__(self, info: SystemInfo):
        raise NotImplementedError("Subclasses must implement __run__()")

    def __post_run__(self):
        sys.stdout.write("\r" + " " * PADDING + "\r")
        sys.stdout.write(self.format_summary() + "\n")
        sys.stdout.flush()


class GPUCheck(Check):

    def __init__(self):
        super(GPUCheck, self).__init__("Cheking GPU")

    def __run__(self, info):
        info.collect_gpu_info()

        if not info.gpus:
            self.status = CheckStatus.FAIL
            self.message = "No GPUs detected"
            return

        for gpu in info.gpus:
            if gpu.description is None or gpu.subsystem is None:
                self.status = CheckStatus.FAIL
                self.message = "GPU info incomplete: description or subsystem missing"
                return

        self.status = CheckStatus.OK


class DriverCheck(Check):

    def __init__(self):
        super(DriverCheck, self).__init__("Cheking driver")

    def __run__(self, info):
        for gpu in info.gpus:
            if gpu.description is None or gpu.kernel_module_in_use is None:
                self.status = CheckStatus.FAIL
                self.message = "Driver info missing for GPU '{}'".format(
                    gpu.subsystem or "[unknown]"
                )
                return

            if "NVIDIA" in gpu.description and gpu.kernel_module_in_use not in (
                "nvidia",
                "nouveau",
            ):
                self.status = CheckStatus.FAIL
                self.message = "NVIDIA GPU '{}' uses unsupported driver '{}'".format(
                    gpu.subsystem or "[unknown]", gpu.kernel_module_in_use
                )
                return

        self.status = CheckStatus.OK


class GlxInfoCheck(Check):
    def __init__(self):
        super(GlxInfoCheck, self).__init__("Checking glxinfo")

    def __run__(self, info):
        info.collect_glx_info()
        gl = info.glxinfo
        if gl is None or gl.renderer is None:
            self.status = CheckStatus.FAIL
            self.message = "OpenGL renderer info not available"
            return

        if "llvmpipe" in gl.renderer.lower() or "softpipe" in gl.renderer.lower():
            self.status = CheckStatus.WARNING
            self.message = "Software renderer detected: '{}'".format(gl.renderer)
            return

        if gl.version is None:
            self.status = CheckStatus.FAIL
            self.message = "Failed to get OpenGL version"
            return

        if (
            gl.version.major is None
            or gl.version.minor is None
            or gl.version.major < 4
            or gl.version.minor < 3
        ):
            self.status = CheckStatus.FAIL
            self.message = "OpenGL version too low: '{}.{}'".format(
                gl.version.major, gl.version.minor
            )
            return

        self.status = CheckStatus.OK


def run_checks():
    TextColor.enable()
    info = SystemInfo()
    info.collect_os_info()
    GPUCheck().run(info)
    DriverCheck().run(info)
    GlxInfoCheck().run(info)
