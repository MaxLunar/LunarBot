# -*- coding: utf-8 -*-
import vk_api
import os
import sys
import time
import importlib
import importlib.machinery
import json
from vk_api.longpoll import VkLongPoll, VkEventType

def main():
    ##################
    # Pre-init phase #
    def log(level, message):
        print('[{0} | {1}] {2}'.format(time.strftime("%H:%M:%S"), level, message))
    
    WORK_DIR = sys.path[0]
    MODULES_DIR = WORK_DIR + "/modules/"
    CONFIG_FILE = WORK_DIR + "/bot_config.cfg"

    if not os.path.exists(CONFIG_FILE):
        log('WARN', 'Configuration file is missing or has another name, creating new one...')
        open(CONFIG_FILE, 'w') 
    
    if not os.path.exists(MODULES_DIR):
        log('WARN', 'Missing modules directory/invalid name, creating new one...')
        os.mkdir(MODULES_DIR)

    if not os.listdir(MODULES_DIR):
        log('WARN', 'Bot is actually useless without modules, consider making some of them.')

    class BotLocker:
        def __init__(self, modules_dir=MODULES_DIR, config=CONFIG_FILE, work_dir=WORK_DIR):
            self.work_dir = work_dir
            log('INFO', 'Creating BotLocker instance...')
            self.config_file = config
            self.config = json.load(open(config, 'r'))
            
            self.login = self.config['login']
            self.password = self.config['password']
            
            self.modules_dir = MODULES_DIR
            self.sources = {}
            self.modules = {}
            self.module_list = {}
            
            self.greetings = self.config['greetings']
            self.access = self.config['access']
            self.autoload = self.config['autoload']

            self.lvl_map = {'banned': 0, 'user': 1, 'moder': 2, 'admin': 3, 'superadmin': 4}
            self.unwrap_lvl = lambda lvl: self.lvl_map[lvl]
            
            for mod in self.autoload:
                self.load(mod)

        def update_cfg(self):
            with open(self.config_file, 'r') as cfg:
                self.config = json.load(cfg)
            self.greetings = self.config['greetings']
            self.access = self.config['access']

        def write_cfg(self):
            with open(self.config_file, 'w') as cfg:
                json.dump(self.config, cfg, ensure_ascii=False, indent=4, sort_keys=False)
        
        def update_list(self):
            for module in filter(lambda x: x not in ['example_module', '__disabled__'], os.listdir(self.modules_dir)):
                mod_prefix = None
                try:
                    with open(self.modules_dir + module + '/' + 'prefix.cfg', 'r') as prefixes:
                        mod_prefix = {module: prefixes.read().split('\n')}
                except Exception as err:
                    print(err)
                    continue
                self.module_list.update(mod_prefix)
        
        def load(self, module):
            self.update_list()
            
            if module in self.modules.keys():
                log('ERROR', 'Module "{0}" is already loaded.'.format(module))
                return -1
            
            for prefix in self.module_list.keys():
                if module in self.module_list[prefix]:
                    path = self.modules_dir + prefix + '/main.py'
                    self.sources.update(\
                {prefix: importlib.machinery.SourceFileLoader(prefix, path).load_module()})
                    
                    for name in self.module_list[prefix]:
                        self.modules.update({name: self.sources[prefix]})
                    log('INFO', 'Successfully loaded "{0}" module.'.format(prefix))
                    return 1
            log('ERROR', 'No such module: "{0}".'.format(module))
            return 0

        def unload(self, module):
            if not module in self.modules.keys():
                if not module in sum(self.module_list.values(), []):
                    log('ERROR', 'Module "{0}" doesn\'t exist.'.format(module))
                    return 0
                log('ERROR', 'Module "{0}" isn\'t loaded or doesn\'t exist.'.format(module))
                return -1
            
            for prefix in self.module_list.keys():
                if module in self.module_list[prefix]:
                    try:
                        self.sources[prefix].terminate()
                    except:
                        pass
                    self.sources.pop(prefix)
                    
                    for name in self.module_list[prefix]:
                        self.modules.pop(name)
                    del sys.modules[prefix]
                    log('INFO', 'Successfully unloaded "{0}" module.'.format(module))
                    return 1

        def reload(self, module):
            if not module in self.modules.keys():
                if not module in sum(self.module_list.values(), []):
                    log('ERROR', 'Module "{0}" doesn\'t exist.'.format(module))
                    return 0
                log('ERROR', 'Module "{0}" isn\'t loaded.'.format(module))
                return -1
            
            if module in self.sources.keys():
                try:
                    self.sources[module].terminate()
                except:
                    pass
                del sys.modules[module]
                importlib.invalidate_caches()
                
                path = self.modules_dir + module + '/main.py'
                self.sources[module] = importlib.machinery.SourceFileLoader(module, path).load_module()
                
                for key in self.module_list[module]:
                    self.modules.update({key: self.sources[module]})
                log('INFO', 'Successfully reloaded "{0}" module.'.format(module))
                return 1
        
        def call(self, module, **kw):
            try:
                level = self.unwrap_lvl('user')
                for acc in self.access.keys():
                    if kw['event'].user_id in self.access[acc]:
                        level = self.unwrap_lvl(acc)
                        break
                if self.unwrap_lvl(self.modules[module].access) <= level:
                    self.modules[module].call(**kw)
                    return True
            except Exception as error:
                print(error)
                return False
        

    ##################

    bot = BotLocker()

    vk_session = vk_api.VkApi(bot.login, bot.password)

    try:
        log('INFO', 'Attempting to authorize...')
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        log('ERROR', 'There was an error during the authorization:')
        print(error_msg)
        return

    log('INFO', 'Successfully authorized, getting API and starting LongPoll session...')

    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    log('INFO', 'LongPoll session started successfully.')

    #####################
    # Utility functions #
    
    def simple_reply(msg):
        vk.messages.send(
                peer_id=event.peer_id,
                message=msg,
                forward_messages=event.message_id
                )

    #####################

    for event in longpoll.listen():
        log('BOT_INFO', 'Logging incoming event...')
        if event.type == VkEventType.MESSAGE_NEW:
            print('Новое сообщение:')

            if event.from_me:
                print('От меня для: ', end='')
            elif event.to_me:
                print('Для меня от: ', end='')

            if event.from_user:
                print(event.user_id)
            elif event.from_chat:
                print(event.user_id, 'в беседе', event.chat_id)
            elif event.from_group:
                print('группы', event.group_id)

            print('Текст: ', event.text)
            print()
            
            #########################
            # Responses to messages #
            if not event.text and event.user_id in bot.access['banned']:
                continue

            msg = list(filter(None, event.text.split()))

            if not msg:
                continue

            if msg[0].lower() in bot.greetings and len(msg) != 1:
                command, options = msg[1].lower(), msg[2:]
                
                if event.user_id in bot.access['superadmin']:
                    if command == 'load' and options:
                        result = bot.load(options[0])
                        
                        if result == 1:
                            simple_reply('Модуль "{0}" успешно загружен.'.format(options[0]))
                        elif result == 0:
                            simple_reply('Модуль "{0}" не существует.'.format(options[0]))
                        elif result == -1:
                            simple_reply('Модуль "{0}" уже загружен'.format(options[0]))
                    
                    if command == 'unload' and options:
                        result = bot.unload(options[0])
                        
                        if result == 1:
                            simple_reply('Модуль "{0}" успешно выгружен.'.format(options[0]))
                        elif result == 0:
                            simple_reply('Модуль "{0}" не существует.'.format(options[0]))
                        elif result == -1:
                            simple_reply('Модуль "{0}" не загружен в данный момент.'.format(options[0]))
                    if command == 'reload' and options:
                        result = bot.reload(options[0])
                        
                        if result == 1:
                            simple_reply('Модуль "{0}" успешно перезагружен.'.format(options[0]))
                        elif result == 0:
                            simple_reply('Модуль "{0}" не существует.'.format(options[0]))
                        elif result == -1:
                            simple_reply('Модуль "{0}" не загружен в данный момент'.format(options[0]))

                if command in bot.modules.keys():
                    bot.call(module=command, vk=vk, vk_session=vk_session, event=event, bot=bot)
                #########################


        elif event.type == VkEventType.USER_TYPING:
            print('Печатает ', end='')

            if event.from_user:
                print(event.user_id)
            elif event.from_group:
                print('администратор группы', event.group_id)

        elif event.type == VkEventType.USER_TYPING_IN_CHAT:
            print('Печатает ', event.user_id, 'в беседе', event.chat_id)

        elif event.type == VkEventType.USER_ONLINE:
            print('Пользователь', event.user_id, 'онлайн', event.platform)
 
        elif event.type == VkEventType.USER_OFFLINE:
            print('Пользователь', event.user_id, 'оффлайн', event.offline_type)
 
        else:
            print(event.type, event.raw[1:])

if __name__ == '__main__':
    main()
