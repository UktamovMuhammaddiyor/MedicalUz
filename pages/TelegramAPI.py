import json
import requests
from .creditionals import BOT_URL, URL


def sentMessage(chat_id, text, reply_markup={}, parse_mode='HTML', url=''):
    """ send message to telegram user with chat_id """

    if type(reply_markup) == list:
        reply_markup = {
            reply_markup[0]: [[{'text': i[0], 'callback_data': i[1]} for i in reply_markup[1][son]]
                              for son in range(len(reply_markup[1]))]
        }
    return requests.post(BOT_URL + 'sendMessage', {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'reply_markup': json.dumps(reply_markup)
    }).json()


def sendPhoto(chat_id, caption, photo, reply_markup={}, parse_mode=''):
    """ send Photo to user with chat_id """

    if type(reply_markup) == list:
        reply_markup = {
            reply_markup[0]: [[{'text': i[0], 'callback_data': i[1]} for i in reply_markup[1][son]]
                              for son in range(len(reply_markup[1]))]
        }

    return requests.post(BOT_URL + 'sendPhoto', {
        'chat_id': chat_id,
        'caption': caption,
        'photo': photo,
        'parse_mode': parse_mode,
        'reply_markup': json.dumps(reply_markup)
    })


def sendDocument(chat_id, caption, document, thumb='', reply_markup={}, parse_mode=''):
    """ send message to telegram user with chat_id """

    if type(reply_markup) == list:
        reply_markup = {
            reply_markup[0]: [[{'text': i[0], 'callback_data': i[1]} for i in reply_markup[1][son]]
                              for son in range(len(reply_markup[1]))]
        }

    return requests.post(BOT_URL + 'sendDocument', {
        'chat_id': chat_id,
        'caption': caption,
        'document': document,
        'thumb': thumb,
        'parse_mode': parse_mode,
        'reply_markup': json.dumps(reply_markup)
    })


def deleteMessage(chat_id, message_id):
    """ delete message with message_id in chat_id """

    return requests.post(BOT_URL + 'deleteMessage', {
        'chat_id': chat_id,
        'message_id': message_id,
    })


def editMessage(chat_id, message_id, text, reply_markup={}, parse_mode='HTML'):
    """ edit message with message_id in chat_id """

    if type(reply_markup) == list:
        reply_markup = {
            reply_markup[0]: [[{'text': i[0], 'callback_data': i[1]} for i in reply_markup[1][son]]
                              for son in range(len(reply_markup[1]))]
        }
    return requests.post(BOT_URL + 'editMessageText', {
        'chat_id': chat_id,
        'message_id': message_id,
        'parse_mode': parse_mode,
        'text': text,
        'reply_markup': json.dumps(reply_markup),
    }).json()


def askPhoneNumber(chat_id, text, reply_markup):
    """ ask user phone number """

    return requests.post(BOT_URL + 'sendMessage', {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': json.dumps({
            'keyboard': [[{'text': reply_markup, 'request_contact': True}]],
            'resize_keyboard': True,
            'one_time_keyboard': True,
        }),
    })

# now don't need
# def searchMedicine(name, city):
#     medicines = Medicines.objects.filter(medicine_name__icontains=name)
#     true_med = []
#     for medicine in medicines:
#         if medicine.address.city.name == city:
#             true_med.append(medicine)
#     son = 1
#     for med in true_med:
#         print(f"{son} Dorixona {med.address.name}\nManzil: {med.address.address}\nIshlab chiqaruvchi: {med.manufacturer}\nNarxi: {med.price} so'm\nTel nomer: {med.address.phone_number}")
#         son += 1
#     return true_med
