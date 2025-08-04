from .analyser import run_checks
from .config import parse_args, create_dirs
from .logging import init_file_logger
from .report import create_report
import tempfile
import shutil


def main():
    log_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".log", prefix="ghc_")
    init_file_logger(log_file)
    config = parse_args()
    create_dirs(config)
    run_checks(config)
    create_report(config, log_file)
    if not config.no_clear:
        shutil.rmtree(config.temp_dir)


if __name__ == "__main__":
    main()
