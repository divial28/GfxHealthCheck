import shutil
import os


def create_report(tmp_dir: str, log_file):
    # create archive here
    log_file.flush()
    shutil.copy(log_file.name, os.path.join(tmp_dir, "gfx_health.log"))
