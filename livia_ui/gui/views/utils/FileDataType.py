import os


class FileDataType:
    def __init__(self, path: str):
        self._path: str = path

    @property
    def path(self) -> str:
        return self._path

    @staticmethod
    def can_manage(path: str) -> bool:
        return os.path.exists(path)
