from .system_info import SystemInfo
from .logging import TextColor

success = lambda: TextColor.green("✔")
warning = lambda: TextColor.yellow("⚠")
fail = lambda: TextColor.red("❌")


class CheckResult(object):
    def __init__(self, name, passed, message=None):
        self.name: str = name
        self.passed: bool = passed
        self.message: str = message or ""

    def is_ok(self):
        return self.passed

    def format_summary(self, padding=30):
        status = success() if self.passed else fail()
        line = self.name.ljust(padding) + status
        if not self.passed and self.message:
            line += "\n   ↳ " + self.message
        return line


def check_gpu(info: SystemInfo):
    res = CheckResult("Checking GPU", True)
    if not info.gpus:
        res.passed = False
        res.message = "No GPUs detected"
    return res


def check_driver(info: SystemInfo):
    res = CheckResult("Checking driver", True)
    for gpu in info.gpus:
        if "NVIDIA" in gpu.description and gpu.kernel_module_in_use not in (
            "nvidia",
            "nouveau",
        ):
            res.passed = False
            res.message = (
                "NVIDIA GPU '{}' uses unsupported driver '{}'".format(
                    gpu.name, gpu.driver
                ),
            )
    return res


def run_checks():
    TextColor.enable()

    results = []
    info = SystemInfo()
    info.collect_uname()
    info.collect_gpu_info()
    results.append(check_gpu(info))
    results.append(check_driver(info))
    for result in results:
        print(result.format_summary())
