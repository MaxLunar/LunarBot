# NOTE: call function is IMPORTANT for each module
#       terminate function required for modules working with files, etc., just to close them and finish work
#       each module receives next data:
#       "vk" object - vk_api.VkApi().get_api() object to work with VK API
#       "vk_session" object - authorized vk_api.VkApi() object to use with VkUpload etc.
#       "event" object - Event() object from longpoll.listen() to get message related data (message_id, text, etc.)
#       "bot" object - BotLocker() object to get config related data (access list, etc.)

documentation = """example_module - This is example documentation. Can be used for implementing the help command.
This module exists only for example purposes."""

access = 'user' # access level of this command. Can be used to restrict some users from using specific commands

def terminate():
    # Store all files and objects in variables/dictionary from global namespace, to ensure visibility
    pass

def call(**kw):
    vk = kw['vk']
    event = kw['event']
    # Unpack only those elements you need (vk and event is probably required to normally process the request from user)
    # Next unpacks is unnecessary for proper work and only here to show their existence(decide it yourself)
    vk_session = kw['vk_session']
    bot = kw['bot']
    try:
        # do something
        pass
    except Exception as err:
        print(err)
        return False
