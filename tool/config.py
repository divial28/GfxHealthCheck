from .utils import force_mkdir
import argparse
import os
import tempfile


class Config(object):
    def __init__(self):
        self.report_dir = tempfile.gettempdir() # type: str
        self.temp_dir = tempfile.gettempdir() # type: str
        self.no_clear = False # type: bool


def parse_args() -> Config:
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
    parser.add_argument("--no-clear", action='store_true', help="dont clear TEMP_DIR after finish")
    args = parser.parse_args()
    config.report_dir = args.report_dir
    config.temp_dir = os.path.join(args.temp_dir, "gfx-health-report")
    config.no_clear = args.no_clear
    return config


def create_dirs(config: Config):
    try:
        dirs = {config.temp_dir}
        for dir in dirs:
            force_mkdir(dir)
    except PermissionError as e:
        print(e)
        exit(-1)
