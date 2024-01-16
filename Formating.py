from Dictionary import dict

def Split(message, separator):
    if message[-1] == '.':
        message = message[:-1:]
        message = message.split(separator)
    else: message = message.split(separator)
    return message

def DeleteSpace(message):
    if type(message) == str:
        while message[0] == " ":
            message = message[1::]
        while message[-1] == " ":
            message = message[:-1:]
    elif type(message) == list:
        for index in range(len(message)):
            while message[index][0] == " ":
                message[index] = message[index][1::]
            while message[index][-1] == " ":
                message[index] = message[index][:-1:]
    return message

def Capitalize(message):
    message = DeleteSpace(message)
    if type(message) == str:
        if message[0].islower() == True:
            message = message.capitalize()
    elif type(message) == list:
        for index in range(len(message)):
            if message[index][0].islower() == True:
                message[index] = message[index].capitalize()
    return message

def Point(message):
    message = Capitalize(message)
    if type(message) == str:
        if message[-1] != ".":
            message = "{0}. ".format(message)
    elif type(message) == list:
        for index in range(len(message)):
            if message[index][-1] != ".":
                message[index] = "{0}. ".format(message[index])
    return message

def DescriptFormating(message) -> list:
    message = Point(Split(message,'.'))
    return message

def StepsFormating(message) -> list:
    message = Point(Split(message,'.'))
    for index in range(len(message)):
        message[index] = f"\n{index+1}) " + message[index]
    return message

def PlatformFormating(message) -> list:
    message = DeleteSpace(Split(message, '.'))
    platform = {v: k for k, values in dict.items() for v in values}
    for index in range(len(message)):
        message[index] = platform.get(message[index], message[index]) + ".\n"
    return message

def about_text() -> str:
    message = "This bot is designed to create bug reports while testing.\n\nThe proposed structure consists of media file (image or video), title, description, reproduction steps, severity and bug detection environment.\n\nType the command '<b>/start</b>' to start the creation. You can skip the bug report field by typing the word '<code>pass</code>' in the message.\n\nTo cancel the creation, enter the command '<b>/cancel</b>'. Canceling will delete some messages in chat with the bot.\n\nContact the owner for more information: @vat1kan."
    return message

def dict_values()-> str:
    message = "Here is a list of abbreviations/synonyms for bug detection environment. When creating a bug report, it is enough to specify the corresponding abbreviation for automatic conversion into the environment name.\n"
    for key, values in dict.items():
        message += f"\n<b>{key}:</b>\n{', '.join(values)}, \n"
    return message
    