from .config import Config
from .utils import create_acrhive
import os
import shutil


def create_report(config: Config, log_file):
    log_file.flush()
    shutil.copy(log_file.name, os.path.join(config.temp_dir, "gfx_health.log"))
    report_path = os.path.join(config.report_dir, "gfx_health_report.tar.gz")
    create_acrhive(config.temp_dir, report_path)
    print("report path: {}".format(report_path))
