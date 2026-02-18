__all__ = ["run"]


def run(argv=None):
    from .cli import run as _run

    return _run(argv)
