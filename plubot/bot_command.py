from collections import defaultdict
from typing import Optional, List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from plubot.plugin.hook_types import HookCommandsInfoReturnType

from telegram import BotCommandScopeChat, BotCommandScope, BotCommandScopeDefault


class BotCommandInfo:
    command: str
    description: str
    scope: Optional[Union[List[BotCommandScope], BotCommandScope]]
    language_code: Optional[str]

    def __init__(self, command, description, scope=None, language_code=None):
        self.command = command
        self.description = description
        self.scope = scope or BotCommandScopeDefault()
        self.language_code = language_code

    @property
    def bot_command(self):
        return tuple([self.command, self.description])


def group_bot_command_info(commands_info_list: List['HookCommandsInfoReturnType']):
    """
    >>> group_bot_command_info([[['help', 'help description'], BotCommandInfo('foo', 'Foo')]])
    [{'scope': None, 'language_code': None, \
'commands': [('help', 'help description'), ('foo', 'Foo')]}]
    >>> group_bot_command_info([[ # doctest: +ELLIPSIS
    ... BotCommandInfo('foo', 'Foo', scope=BotCommandScopeChat(chat_id='@superchat')),
    ... BotCommandInfo('bar', 'Bar', scope=BotCommandScopeChat(chat_id='@superchat')),
    ... ]])
    [{'scope': <telegram.botcommandscope.BotCommandScopeChat object at 0x...>, \
'language_code': None, 'commands': [('foo', 'Foo'), ('bar', 'Bar')]}]
    """
    flatten_list = [ci for ci_list in commands_info_list for ci in ci_list]
    group_map = defaultdict(list)
    scope_map = dict()
    for ci in flatten_list:
        if isinstance(ci, (list, tuple)):
            ci = BotCommandInfo(*ci)
        scopes = ci.scope
        if not isinstance(scopes, list):
            scopes = [scopes]
        lang_code = ci.language_code
        if lang_code == 'en':
            lang_code = None
        for scope in scopes:
            scope_hash = str(scope and scope.to_dict())
            scope_map[scope_hash] = scope
            group_map[(scope_hash, lang_code)].append(ci.bot_command)

    if len(scope_map) > 1:
        for [[scope_hash, lang_code], commands] in group_map.items():
            scope = scope_map[scope_hash]
            if scope.type == BotCommandScope.DEFAULT:
                for s_h, s in scope_map.items():
                    if s_h == scope_hash:
                        continue
                    group_map[(s_h, lang_code)].extend(commands)

    groups = []
    for [[scope_hash, lang_code], commands] in group_map.items():
        scope = scope_map[scope_hash]
        scopes = [scope]
        commands = sorted(set(commands), key=lambda i: commands.index(i))
        for s in scopes:
            groups.append({
                'scope': s,
                'language_code': lang_code,
                'commands': commands,
            })
    return groups
