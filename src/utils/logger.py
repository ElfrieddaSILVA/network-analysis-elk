
class TColor:
    ENDC = '\033[0m'
    WARN = '\033[93m'
    OK   = '\033[92m'
    ERR = '\033[91m'


class Logger:
    @staticmethod
    def warn(msg: str, **kwargs):
        print(TColor.WARN + str(msg) + TColor.ENDC, **kwargs)

    @staticmethod
    def ok(msg: str, **kwargs):
        print(TColor.OK + str(msg) + TColor.ENDC, **kwargs)

    @staticmethod
    def error(msg: str, **kwargs):
        print(TColor.ERR + str(msg) + TColor.ENDC, **kwargs)

