from .utils import run
from shutil import which
from typing import List
import re
import subprocess


class GpuInfo:
    def __init__(
        self,
        description=None,
        kernel_module_in_use=None,
        kernel_modules=None,
        subsystem=None,
    ):
        self.description: str = description
        self.kernel_module_in_use: str = kernel_module_in_use
        self.kernel_modules: str = kernel_modules or []
        self.subsystem: str = subsystem

    @staticmethod
    def from_lspci_strings(lines: list[str]) -> "GpuInfo":
        if not lines:
            return GpuInfo(description="[missing lspci block]")

        description = lines[0].strip()
        kv_map = {}

        for line in lines[1:]:
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            kv_map[key.strip()] = val.strip()

        return GpuInfo(
            description=description,
            kernel_module_in_use=kv_map.get("Kernel driver in use"),
            kernel_modules=[
                x.strip()
                for x in kv_map.get("Kernel modules", "").split(",")
                if x.strip()
            ],
            subsystem=kv_map.get("Subsystem"),
        )

    def to_dict(self):
        return {
            "description": self.description,
            "kernel_module_in_use": self.kernel_module_in_use,
            "kernel_modules": self.kernel_modules,
            "subsystem": self.subsystem,
        }


class SystemInfo(object):
    def __init__(self):
        self.os_name: str = None
        self.os_version: str = None
        self.arch: str = None
        self.gpus: List[GpuInfo] = []

    def collect_uname(self):
        try:
            output = run(["uname", "-rms"])
            parts = output.split()
            if len(parts) == 3:
                self.os_name = parts[0]
                self.os_version = parts[1]
                self.arch = parts[2]
            else:
                self.os_name = self.os_version = self.arch = "[unexpected uname output]"
        except Exception as e:
            self.os_name = self.os_version = self.arch = "[error: {}]".format(e)

    def collect_gpu_info(self):
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
            self.gpus = [GpuInfo.from_lspci_strings(block) for block in gpu_blocks]

        except Exception as e:
            self.gpus = [
                GpuInfo(
                    name="[error: {}]".format(e),
                    kernel_driver="[error: {}]".format(e),
                )
            ]

    def to_dict(self):
        return {
            "os_name": self.os_name,
            "os_version": self.os_version,
            "arch": self.arch,
            "gpus": [gpu.to_dict() for gpu in self.gpus],
        }
