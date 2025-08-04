from .utils import force_mkdir
import argparse
import os
import tempfile


class Config(object):
    def __init__(self):
        self.report_dir: str = tempfile.gettempdir()
        self.temp_dir: str = tempfile.gettempdir()


def parse_args():
    config = Config()
    parser = argparse.ArgumentParser(
        prog="GfxHealthCheck",
        description="A tool to collect and analyse different gpu related info and help fix gfx related problems and setup system properly",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--report-dir",
        required=False,
        type=str,
        default=config.report_dir,
        help="directory to place report archive",
    )
    parser.add_argument(
        "--temp-dir",
        required=False,
        type=str,
        default=config.temp_dir,
        help="directory to store all temporary files",
    )
    args = parser.parse_args()
    config.report_dir = args.report_dir
    config.temp_dir = args.temp_dir + "gfx-health"
    return config


def create_dirs(config: Config):
    try:
        dirs = {config.temp_dir}
        for dir in dirs:
            force_mkdir(dir)
    except PermissionError as e:
        print(e)
        exit(-1)
