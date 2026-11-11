"""The messages that ``text`` shares with every command."""

from typing import Final

from recipe_menu.text._message import Message

RUN_CHECK: Final[Message] = Message(
    'Run "recipe-menu check" to see every problem.',
    "运行“recipe-menu check”查看所有问题。",
)
RUN_HELP_FOR_OPTIONS: Final[Message] = Message(
    'Run "recipe-menu --help" to see the options.',
    "运行“recipe-menu --help”查看选项。",
)
RUN_HELP_FOR_COMMANDS: Final[Message] = Message(
    'Run "recipe-menu --help" to see the commands.',
    "运行“recipe-menu --help”查看命令。",
)
