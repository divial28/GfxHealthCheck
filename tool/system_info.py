from .utils import run
from typing import List
import re


class ErrorContext(object):
    def __init__(self):
        self.os_parse_error: str = None
        self.gpu_info_parse_error: str = None
        self.opengl_info_parse_error: str = None
        self.opengl_version_parse_error: str = None


class GpuInfo:
    def __init__(self):
        self.description: str = None
        self.kernel_module_in_use: str = None
        self.kernel_modules: str = None
        self.subsystem: str = None

    @staticmethod
    def from_lspci_strings(err_ctx: ErrorContext, lines: list[str]) -> "GpuInfo":
        description = lines[0].strip()
        kv_map = {}
        for line in lines[1:]:
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            kv_map[key.strip()] = val.strip()

        info = GpuInfo()
        info.description = (description,)
        info.kernel_module_in_use = (kv_map.get("Kernel driver in use"),)
        for x in kv_map.get("Kernel modules", "").split(","):
            info.kernel_modules.append(x.strip())
        info.subsystem = (kv_map.get("Subsystem"),)
        return info


class OpenGLVersion(object):
    def __init__(self):
        self.string: str = None
        self.major: int = None
        self.minor: int = None

    @staticmethod
    def from_string(err_ctx: ErrorContext, version: str) -> tuple[int, int]:
        try:
            firstDot = version.find(".")
            major = int(version[firstDot - 1])
            secondDot = version.find(".", firstDot + 1)
            minor = int(version[secondDot - 1])
            return major, minor
        except Exception as e:
            err_ctx.opengl_version_parse_error = str(e)
            return None, None


class OpenGLInfo(object):
    def __init__(self):
        self.vendor: str = None
        self.renderer: str = None
        self.version: OpenGLVersion = None


class SystemInfo(object):
    def __init__(self):
        self.os_name: str = None
        self.os_version: str = None
        self.arch: str = None
        self.gpus_info: List[GpuInfo] = None
        self.opengl_info = None

    def collect_os_info(self, err_ctx: ErrorContext):
        try:
            output = run(["uname", "-rms"])
            parts = output.split()
            if len(parts) == 3:
                self.os_name = parts[0]
                self.os_version = parts[1]
                self.arch = parts[2]
            else:
                err_ctx.os_parse_error = "unexpected `uname` output: " + output
                self.os_name = self.os_version = self.arch = None

        except Exception as e:
            err_ctx.os_parse_error = str(e)
            self.os_name = self.os_version = self.arch = None

    def collect_gpu_info(self, err_ctx: ErrorContext):
        try:
            output = run(["lspci", "-k"])
            lines = output.splitlines()
            blocks = []
            current_block = []

            for line in lines:
                if line and not re.match(r"^\s+", line):
                    if current_block:
                        blocks.append(current_block)
                    current_block = [line]
                else:
                    current_block.append(line)

            if current_block:
                blocks.append(current_block)

            gpu_blocks = [b for b in blocks if any("VGA" in l or "3D" in l for l in b)]
            self.gpus_info = [
                GpuInfo.from_lspci_strings(err_ctx, block) for block in gpu_blocks
            ]

        except Exception as e:
            err_ctx.gpu_info_parse_error = str(e)
            self.gpus_info = None

    def collect_glx_info(self, err_ctx: ErrorContext):
        try:
            info = OpenGLInfo()
            version = OpenGLVersion()
            output = run(["glxinfo"])
            for line in output.splitlines():
                if "OpenGL vendor string" in line:
                    info.vendor = line.split(":", 1)[1].strip()
                elif "OpenGL renderer string" in line:
                    info.renderer = line.split(":", 1)[1].strip()
                elif "OpenGL version string" in line:
                    version.string = line.split(":", 1)[1].strip()
            version.major, version.minor = OpenGLVersion.from_string(
                err_ctx, version.string
            )
            info.version = version
            self.opengl_info = info
        except Exception as e:
            err_ctx.opengl_info_parse_error = str(e)
            self.opengl_info = OpenGLInfo()
