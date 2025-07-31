from .system_info import SystemInfo
from .logging import TextColor
import sys

success = lambda: TextColor.green("✔")
warning = lambda: TextColor.yellow("⚠")
fail = lambda: TextColor.red("❌")

PADDING = 40


class Check(object):

    def __init__(self, label="", passed=True, message=None):
        self.label: str = label
        self.passed: bool = passed
        self.message: str = message or ""

    def run(self, info: SystemInfo):
        self.__pre_run__()
        self.__run__(info)
        self.__post_run__()

    def is_ok(self):
        return self.passed

    def format_summary(self, padding=PADDING):
        status = success() if self.passed else fail()
        line = self.label.ljust(padding) + status
        if not self.passed and self.message:
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
        super().__init__()
        self.label = "Cheking GPU"

    def __run__(self, info: SystemInfo):
        if not info.gpus:
            self.passed = False
            self.message = "No GPUs detected"


class DriverCheck(Check):

    def __init__(self):
        super().__init__()
        self.label = "Cheking driver"

    def __run__(self, info: SystemInfo):
        for gpu in info.gpus:
            if "NVIDIA" in gpu.description and gpu.kernel_module_in_use not in (
                "nvidia",
                "nouveau",
            ):
                self.passed = False
                self.message = (
                    "NVIDIA GPU '{}' uses unsupported driver '{}'".format(
                        gpu.subsystem, gpu.kernel_module_in_use
                    ),
                )


def run_checks():
    TextColor.enable()
    info = SystemInfo()
    info.collect_uname()
    info.collect_gpu_info()
    GPUCheck().run(info)
    DriverCheck().run(info)
