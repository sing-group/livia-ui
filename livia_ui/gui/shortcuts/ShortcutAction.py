from enum import IntEnum


class ShortcutAction(IntEnum):
    def get_default_shortcut(self) -> str:
        raise NotImplementedError()
