import os
import sys


def resource_path(*parts):
    base_path = getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    return os.path.join(base_path, *parts)


def asset_path(filename):
    return resource_path("assets", filename)
