from .system_info import collect_system_info
from .logger import log


def main():
    log("Starting Graphics System Health Check...")
    sys_info = collect_system_info()
    log("System Info:")
    [log(group, info) for group, info in sys_info.items()]
    log("Health check complete.")


if __name__ == "__main__":
    main()
