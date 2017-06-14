# bonham_core / exceptions

__all__ = ['RequestDenied']


class RequestDenied(BaseException):
    def __init__(self, *args):
        super().__init__(args)
