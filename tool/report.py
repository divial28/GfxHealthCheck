from .config import Config
from .utils import create_acrhive
import os
import shutil


def create_report(config: Config, log_file):
    log_file.flush()
    shutil.copy(log_file.name, os.path.join(config.temp_dir, "gfx_health.log"))
    shutil.copy("/var/log/Xorg.0.log", config.temp_dir)
    shutil.copy("/etc/X11/xorg.conf", config.temp_dir) # might have different name
    shutil.copytree("/etc/X11/xorg.conf.d", os.path.join(config.temp_dir, "xorg.conf.d"))
    shutil.copytree("/etc/modprobe.d", os.path.join(config.temp_dir, "modprobe.d"))
    report_path = os.path.join(config.report_dir, "gfx_health_report.tar.gz")
    create_acrhive(config.temp_dir, report_path)
    print("report path: {}".format(report_path))
