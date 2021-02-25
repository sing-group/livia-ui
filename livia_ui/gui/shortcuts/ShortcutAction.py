from enum import IntEnum


class ShortcutAction(IntEnum):
    def get_default_shortcut(self) -> str:
        raise NotImplementedError()

    def get_label(self) -> str:
        raise NotImplementedError()

    def get_group(self) -> str:
        raise NotImplementedError()

    def get_order(self) -> int:
        raise NotImplementedError()
