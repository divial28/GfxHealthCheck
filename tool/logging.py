import pprint


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
    def green(text):
        return TextColor.GREEN + text + TextColor.RESET

    @staticmethod
    def red(text):
        return TextColor.RED + text + TextColor.RESET

    @staticmethod
    def yellow(text):
        return TextColor.YELLOW + text + TextColor.RESET
