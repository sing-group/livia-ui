from typing import Dict, Set, Union, Tuple, List

from livia.process.listener.EventListeners import EventListeners
from livia_ui.gui.shortcuts.DefaultShortcutAction import DefaultShortcutAction
from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction
from livia_ui.gui.shortcuts.errors.ShortcutActionAlreadyRegisteredError import ShortcutActionAlreadyRegisteredError
from livia_ui.gui.shortcuts.errors.ShortcutUnknownError import ShortcutUnknownError
from livia_ui.gui.status.listener.ShortcutStatusChangeEvent import ShortcutStatusChangeEvent
from livia_ui.gui.status.listener.ShortcutStatusChangeListener import ShortcutStatusChangeListener


class ShortcutStatus:
    def __init__(self,
                 action_keys: Dict[ShortcutAction, Set[str]] =
                 {action: {action.get_default_shortcut()} for action in DefaultShortcutAction}):
        self._action_keys: Dict[ShortcutAction, Set[str]] = action_keys

        self._listeners: EventListeners[ShortcutStatusChangeListener] = EventListeners[
            ShortcutStatusChangeListener]()

    @property
    def shortcuts(self) -> Dict[ShortcutAction, Tuple[str, ...]]:
        return {action: tuple(keys) for action, keys in self._action_keys.items()}

    def get_keys(self, action: ShortcutAction) -> Tuple[str, ...]:
        return tuple(self._action_keys[action])

    def get_groups(self) -> List[str]:
        unique_groups = []
        for action in self._action_keys:
            if action.get_group() not in unique_groups:
                unique_groups.append(action.get_group())
        return unique_groups

    def get_actions_by_group(self, group: str) -> Dict[ShortcutAction, Tuple[str, ...]]:
        return {action: tuple(keys) for action, keys in sorted(self._action_keys.items(),
                                                               key=lambda item: item[0].get_order())
                if action.get_group() == group}

    def add_action(self, action: ShortcutAction, keys: Union[Set[str], str] = set()):
        if self.has_action(action):
            raise ShortcutActionAlreadyRegisteredError(action)
        else:
            self._action_keys[action] = {keys} if isinstance(keys, str) else keys

            event = ShortcutStatusChangeEvent(self, action, None, self._action_keys[action])
            for listener in self._listeners:
                listener.shortcut_added(event)

    def remove_action(self, action: ShortcutAction):
        if self.has_action(action):
            keys = self._action_keys[action]
            del self._action_keys[action]

            event = ShortcutStatusChangeEvent(self, action, keys, None)
            for listener in self._listeners:
                listener.shortcut_removed(event)
        else:
            raise ShortcutUnknownError(action)

    def has_action(self, action: ShortcutAction) -> bool:
        return action in self._action_keys

    def add_keys(self, action: ShortcutAction, keys: Union[Set[str], str]):
        if self.has_action(action):
            current_keys = self._action_keys[action]

            if not current_keys.issuperset(keys):
                old_keys = tuple(current_keys)
                self._action_keys[action].update({keys} if isinstance(keys, str) else keys)
                new_keys = self._action_keys[action]

                event = ShortcutStatusChangeEvent(self, action, old_keys, new_keys)
                for listener in self._listeners:
                    listener.shortcut_modified(event)
        else:
            raise ShortcutUnknownError(action)

    def set_keys(self, action: ShortcutAction, keys: Union[Set[str], str]):
        if self.has_action(action):
            current_keys = self._action_keys[action]

            if not current_keys.issuperset(keys):
                old_keys = tuple(current_keys)
                self._action_keys[action] = {keys} if isinstance(keys, str) else keys
                new_keys = self._action_keys[action]

                event = ShortcutStatusChangeEvent(self, action, old_keys, new_keys)
                for listener in self._listeners:
                    listener.shortcut_modified(event)
        else:
            raise ShortcutUnknownError(action)

    def remove_keys(self, action: ShortcutAction, keys: Union[Set[str], str]):
        if self.has_action(action):
            current_keys = self._action_keys[action]

            if any(current_keys.union(keys)):
                old_keys = tuple(current_keys)
                self._action_keys[action].difference_update({keys} if isinstance(keys, str) else keys)
                new_keys = self._action_keys[action]

                event = ShortcutStatusChangeEvent(self, action, old_keys, new_keys)
                for listener in self._listeners:
                    listener.shortcut_modified(event)
        else:
            raise ShortcutUnknownError(action)

    def add_shortcut_configuration_change_listener(self, listener: ShortcutStatusChangeListener):
        self._listeners.append(listener)

    def remove_shortcut_configuration_change_listener(self, listener: ShortcutStatusChangeListener):
        self._listeners.remove(listener)

    def has_shortcut_configuration_change_listener(self, listener: ShortcutStatusChangeListener) -> bool:
        return listener in self._listeners
