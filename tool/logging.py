import sys


class TextColor:
    GREEN = ""
    RED = ""
    YELLOW = ""
    RESET = ""

    @staticmethod
    def enable():
        TextColor.GREEN = "\033[92m"
        TextColor.RED = "\033[91m"
        TextColor.YELLOW = "\033[93m"
        TextColor.RESET = "\033[0m"

    @staticmethod
    def disable():
        TextColor.GREEN = ""
        TextColor.RED = ""
        TextColor.YELLOW = ""
        TextColor.RESET = ""

    @staticmethod
    def green(text) -> str:
        return TextColor.GREEN + text + TextColor.RESET

    @staticmethod
    def red(text) -> str:
        return TextColor.RED + text + TextColor.RESET

    @staticmethod
    def yellow(text) -> str:
        return TextColor.YELLOW + text + TextColor.RESET


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def init_file_logger(log_file):
    sys.stdout = Tee(sys.stdout, log_file)
    sys.stderr = Tee(sys.stderr, log_file)
