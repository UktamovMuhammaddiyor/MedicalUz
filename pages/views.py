from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from .creditionals import URL, BOT_URL
from .models import Cities, BotUser, Doctor, Admin
from .TelegramAPI import sentMessage, deleteMessage, editMessage, askPhoneNumber, sendPhoto, sendDocument
from .text import text_menu
from .kril_to_lotin import krill_to as t, makeWord
from translate import Translator
from uuid import uuid4
import csv

translater_ru = Translator(to_lang='ru', from_lang='uz')
translater_uz = Translator(to_lang='uz', from_lang='ru')


def index(request):
    return HttpResponse("it's working")


def setWebHook(request):
    """ set webhook for telegram API on URL """

    response = requests.post(BOT_URL + 'setwebhook?url=' + URL).json()
    return HttpResponse(response)


@csrf_exempt
def getpost(request):
    if request.method == 'POST':
        """ reply sent message from user """

        response = json.loads(request.body)
        if 'message' in response:
            response = response['message']
            getUser(response, 'ms')
        elif 'callback_query' in response:
            response = response['callback_query']
            getUser(response, 'cq')
    return HttpResponse('working')


def getUser(response, st):
    """ create user or get user """

    try:
        user = BotUser.objects.get(user_id=response['from']['id'])
    except:
        user = BotUser.objects.create(user_id=response['from']['id'], first_name=response['from']['first_name'])

    if st == 'ms':
        getHandlerMessage(user, response, response['chat']['id'])  # for message
    else:
        getHandlerCQ(user, response, response['message']['chat']['id'])  # for callback_query


def getHandlerMessage(user, response, chat_id):
    """ for get user status and do some functions with status """

    if 'contact' in response.keys():
        addDoctor(user, response, chat_id)
    elif 'text' in response.keys() and response['text'] == '/addAdmin':
        sentMessage(chat_id, 'Okay. Please enter secret password:')
        user.status = 'getAdmin'
        user.save()
    elif 'text' in response.keys() and response['text'] == '/addDoctor':
        # you can add Doctor with /addDoctor command manual
        try:
            doctor = Doctor.objects.filter(user_id=response['from']['id'])
            sentMessage(chat_id, 'Bitta akkauntdan faqat bitta doctor qo"sha olesiz halos. Raxmat.')
        except:
            doctor_ru = Doctor.objects.create(user_id=response['from']['id'], language=1)
            doctor_uz = Doctor.objects.create(user_id=response['from']['id'], language=0)
            doctor_uz.save()
            doctor_ru.save()
            user.status = 'addDoctor'
            user.status_extra = 'getPhone'
            user.save()
            addDoctor(user, response, chat_id)
    elif 'text' in response.keys() and response['text'] == '/add':
        unique_id = uuid4()
        Doctor.objects.create(unique_id=unique_id, language=0)
        Doctor.objects.create(unique_id=unique_id, language=1)
        user.doctor_id = unique_id
        user.status = 'addDoctor'
        user.status_extra = 'getPhone'
        user.save()
        addDoctor(user, response, chat_id)
    elif 'text' in response.keys() and response['text'] == '/set':
        doctors = Doctor.objects.all()
        if set_csv(user, doctors):
            sentMessage(chat_id, 'Done')
        else:
            sentMessage(chat_id, 'error')
    elif user.status == '/start':
        message_id = sentMessage(chat_id, '🇺🇿 Tilni tanlang\n🇷🇺 Выберите язык',
                                 ['inline_keyboard', [[["🇺🇿 O'zbekcha", 'set_uz'], ['🇷🇺 Русский', 'set_ru']]]])
        message_id = message_id['result']['message_id']
        user.callback_data = message_id
        user.save()
    elif user.status == 'nothing':
        deleteMessage(chat_id, user.callback_data)
        sendMenu(user, response, chat_id, 'send')
    elif user.status == 'search_doc':
        deleteMessage(chat_id, user.callback_data)
        sendSearchDoctor(user, response, chat_id, 'send')
    elif user.status == 'searchByName':
        deleteMessage(chat_id, user.callback_data)
        selectCity(user, response, chat_id, 'send')
    elif user.status == 'searchbyname':
        deleteMessage(chat_id, user.callback_data)
        user.previs_status = 'searchbyname'
        user.next_status = 0
        user.next_to_status = 5
        user.save()
        sendResponse(user, chat_id, response, response['text'], 'send', next_status=user.next_status)
    elif user.status == 'addDoctor':
        addDoctor(user, response, chat_id)
    elif user.status == 'getAdmin':
        if 'text' in response.keys():
            if response['text'] == '12211441':
                admin = Admin.objects.create(user_id=response['from']['id'], username=response['from']['first_name'])
                admin.save()
                sentMessage(chat_id, 'you are now an admin.')
            else:
                sentMessage(chat_id, 'Password incorrect')
        else:
            sentMessage(chat_id, 'password incorrect')
        sentMessage(chat_id, 'Main menu: ')
        user.status = 'nothing'
        user.save()
    elif user.status[:11] == 'no_comment_':
        sentMessage(user.status[11:], f"Siz doctor sifatida qabul qilinmadingiz. Sharx:\n<i>{response['text']}</i>",
                    ['inline_keyboard', [[["Operator bilan bog'lanish", f'get_call_{user.status[11:]}']]]])
        sentMessage(chat_id, 'Your message has been sent')
        user.status = 'nothing'
        user.save()


def getHandlerCQ(user, response, chat_id):
    """ for get user callback_query and do some functions with data """

    user_id = response['message']['message_id']
    data = response['data']
    if data == 'search_doc':
        user.previs_status = user.status
        user.status = 'search_doc'
        user.save()
        sendSearchDoctor(user, response['message'], chat_id, '')
    elif data == 'exit':
        if user.previs_status == 'nothing':
            sendMenu(user, response['message'], chat_id, "")
            user.status = 'nothing'
            user.save()
        elif user.previs_status == 'search_doc':
            sendSearchDoctor(user, response['message'], chat_id, '')
            user.status = 'search_doc'
            user.previs_status = 'nothing'
            user.save()
        elif user.previs_status == 'searchByName':
            selectCity(user, response['message'], chat_id, '')
            user.status = 'searchByName'
            user.previs_status = 'search_doc'
            user.save()
        elif user.previs_status == 'searchbyname':
            sendSearchDoctor(user, response['message'], chat_id, '')
            user.status = 'search_doc'
            user.previs_status = 'nothing'
            user.save()
        elif user.previs_status == 'searchByProfession':
            selectCity(user, response['message'], chat_id, '')
            user.status = 'searchByProfession'
            user.previs_status = 'search_doc'
            user.save()
        elif user.previs_status == 'searchProfession':
            user.status = 'searchProfession'
            user.previs_status = 'searchByProfession'
            user.next_status = 0
            user.next_to_status = 5
            user.save()
            selectProfession(user, response['message'], chat_id, '', user.next_status)
    elif data == 'searchByName':
        selectCity(user, response['message'], chat_id, '')
        user.status = 'searchByName'
        user.previs_status = 'search_doc'
        user.save()
    elif data == 'exit_menu':
        sendMenu(user, response['message'], chat_id, '')
        user.status = 'nothing'
        user.save()
    elif data == 'name_exit_menu':
        sendMenu(user, response['message'], chat_id, '')
        deleteMessage(chat_id, response['message']['message_id'])
        user.status = 'nothing'
        user.save()
    elif data == 'name_exit':
        deleteMessage(chat_id, response['message']['message_id'])
    elif data[:11] == 'more_doctor':
        searchByProfession(user, response['message'], chat_id, '', data[11:], user.next_status)
    elif data[:11] == 'next_doctor':
        searchByProfession(user, response['message'], chat_id, '', data[11:], user.next_status)
    elif data[:14] == 'previus_doctor':
        user.next_status = user.next_status - 10
        user.next_to_status = user.next_to_status - 10
        user.save()
        searchByProfession(user, response['message'], chat_id, '', data[14:], user.next_status)
    elif data[:8] == 'more_pro':
        selectProfession(user, response['message'], chat_id, '', next_status=user.next_status)
    elif data[:5] == 'more_':
        sendResponse(user, chat_id, response['message'], data[5:], '', next_status=user.next_status)
    elif data[:8] == 'next_pro':
        selectProfession(user, response['message'], chat_id, '', next_status=user.next_status)
    elif data[:5] == "next_":
        sendResponse(user, chat_id, response['message'], data[5:], '', next_status=user.next_status)
    elif data[:11] == 'previus_pro':
        user.next_status = user.next_status - 10
        user.next_to_status = user.next_to_status - 10
        user.save()
        selectProfession(user, response['message'], chat_id, '', next_status=user.next_status)
    elif data[:8] == 'previus_':
        user.next_status = user.next_status - 10
        user.next_to_status = user.next_to_status - 10
        user.save()
        sendResponse(user, chat_id, response['message'], data[8:], '', next_status=user.next_status)
    elif data == 'searchByProfession':
        selectCity(user, response['message'], chat_id, '')
        user.status = 'searchByProfession'
        user.previs_status = 'search_doc'
        user.save()
    elif data == 'set_ru':
        user.language = 1
        user.status = 'nothing'
        user.save()
        text = 'Привет! Добро пожаловать! 😊\n'
        sendMenu(user, response['message'], chat_id, '', text)
    elif data == 'set_uz':
        user.language = 0
        user.status = 'nothing'
        user.save()
        text = 'Assalomu alaykum! Xush kelibsiz! 😊\n'
        sendMenu(user, response['message'], chat_id, '', text)
    elif data == "change_lang":
        editMessage(chat_id, response['message']['message_id'], '🇺🇿 Tilni tanlang\n🇷🇺 Выберите язык',
                    ['inline_keyboard', [[["🇺🇿 O'zbekcha", 'set_uz'], ['🇷🇺 Русский', 'set_ru']]]])
    elif data[:8] == 'set_city':
        if user.status_extra == 'getPlace2':
            deleteMessage(chat_id, user_id)
            doctor_ru = Doctor.objects.get(unique_id=user.doctor_id, language=1)
            doctor_uz = Doctor.objects.get(unique_id=user.doctor_id, language=0)
            doctor_uz.city = data[8:]
            doctor_uz.save()
            doctor_ru.city = data[8:]
            doctor_ru.save()
            sentMessage(chat_id, "Shifoxona to'liq manzilini yozib qoldiring: ")
            user.status_extra = 'getAddress'
            user.save()
        elif user.status == 'searchByName':
            user.status = 'searchbyname'
            user.status_extra = data[8:]
            user.previs_status = 'searchByName'
            user.save()
            sendsearchByName(user, response['message'], chat_id, '')
        elif user.status == 'searchByProfession':
            user.status = 'searchProfession'
            user.status_extra = data[8:]
            user.previs_status = 'searchByProfession'
            user.next_status = 0
            user.next_to_status = 5
            user.save()
            selectProfession(user, response['message'], chat_id, '', user.next_status)
    elif data == 'no_price':
        deleteMessage(chat_id, user_id)
        doctor_ru = Doctor.objects.get(user_id=response['from']['id'], language=1)
        doctor_uz = Doctor.objects.get(user_id=response['from']['id'], language=0)
        doctor_uz.home_price = "Uyga kelib ko'rmedi"
        doctor_uz.save()
        doctor_ru.home_price = translater_ru.translate("Uyga kelib ko'rmedi")
        doctor_ru.save()
        sentMessage(chat_id, 'Tajribangiz nechi yil.')
        user.status_extra = 'getExperience'
        user.save()
    elif data == 'no_data':
        deleteMessage(chat_id, user_id)
        sentMessage(chat_id, "Siz haqingizdagi ma'lumot adminga jo'natildi. Admin javobini kuting.")
        doctor_ru = Doctor.objects.get(unique_id=user.doctor_id, language=1)
        doctor_uz = Doctor.objects.get(unique_id=user.doctor_id, language=0)
        chat_id2 = sendNotification(user, doctor_uz, doctor_ru)
        sentMessage(chat_id2, "Doctor qo'shilsinmi?",
                    ['inline_keyboard', [[['yes', f'addDoctor_{doctor_uz.unique_id}'],
                                          ['no', f'noDoctor_{doctor_uz.unique_id}']]]])
        user.status = 'nothing'
        user.save()
    elif data[:15] == 'get_profession_':
        user.previs_status = 'searchProfession'
        user.next_status = 0
        user.next_to_status = 5
        user.save()
        searchByProfession(user, response['message'], chat_id, '', data[15:], user.next_status)
    elif data[:9] == 'get_name_':
        sendDoctorByName(user, response['message'], chat_id, '', data[9:])
    elif data[:9] == 'noDoctor_':
        # deleteMessage(chat_id, response['message']['message_id'])
        doctors = Doctor.objects.filter(unique_id=data[9:])
        for doctor in doctors:
            doctor.delete()
        # sentMessage(chat_id, f"User <a href='tg://user?id={data[9:]}'>{data[9:]}</a> has been deleted in server")
        # sentMessage(chat_id, 'Nimaga doctor qabul qilinmadi sharx yozib qoldiring: ')
        sentMessage(chat_id, 'deleted')
        user.status = f"nothing"
        user.save()
    elif data[:9] == 'get_call_':
        editMessage(chat_id, response['message']['message_id'], text_menu['help'][0][user.language])
        admins = Admin.objects.all()
        print(data)
        for admin in admins:
            text = f"User <a href='tg://user?id={data[9:]}'>{user.first_name}</a> " \
                   f"yordam so'rayapti doktor sifatida ro'yhatdan o'tish bo'yicha."
            me = requests.post(BOT_URL + 'sendMessage', {
                'chat_id': admin.user_id,
                'text': text,
                'parse_mode': 'HTML',
                'reply_markup': json.dumps({'inline_keyboard': [[{'text': f'{user.first_name}', 'url': f'tg://user?id={data[9:]}'}]]})
            }).json()
    elif data[:10] == 'addDoctor_':
        # deleteMessage(chat_id, response['message']['message_id'])
        user_id = data[10:]
        doctors = Doctor.objects.filter(unique_id=user_id)
        for doctor in doctors:
            doctor.doctor_status = True
            doctor.save()
        sentMessage(chat_id, f"Doctor muofaqqiyatli qo'shildi:\nDoctor id: <code>{user_id}</code>")
        # sentMessage(data[10:], "Siz Doctor sifatida botga qo'shildingiz")
        user.status = 'nothing'
        user.save()


def addDoctor(user, response, chat_id):
    """ add Doctor collect all information about doctor """

    doctor_uz = Doctor.objects.get(unique_id=user.doctor_id, language=0)
    doctor_ru = Doctor.objects.get(unique_id=user.doctor_id, language=1)
    if user.status_extra == 'getPhone':
        askPhoneNumber(chat_id, text_menu['phone'][0][user.language], text_menu['phone'][1][user.language])
        user.status_extra = 'getName'
        user.save()
    elif user.status_extra == 'getName':
        if 'contact' in response.keys():
            doctor_uz.tel_number = response['contact']['phone_number']
            doctor_ru.tel_number = response['contact']['phone_number']
        else:
            doctor_uz.tel_number = response['text']
            doctor_ru.tel_number = response['text']
        doctor_uz.save()
        doctor_ru.save()
        sentMessage(chat_id, 'Ism familyangizni kiriting(FIO):', {'remove_keyboard': True})
        user.status_extra = 'getPlace'
        user.save()
    elif 'text' in response.keys():
        if user.status_extra == 'getPlace':
            sentMessage(chat_id, 'Qayerda ishlaysiz(Shifoxona nomi):')
            user.status_extra = 'getPlace2'
            user.save()
            doctor_uz.name = response['text']
            doctor_uz.save()
            doctor_ru.name = t(response['text'])
            doctor_ru.save()
        elif user.status_extra == 'getPlace2':
            sentMessage(chat_id, 'Siz ishlaydigon shifoxona qayerda joylashgan: ', ['inline_keyboard', City(user)])
            doctor_uz.working_place = chooseLangUz(user, response) + '("' + response['text'] + '")'
            doctor_uz.save()
            doctor_ru.working_place = chooseLangRu(user, response) + '("' + response['text'] + '")'
            doctor_ru.save()
        elif user.status_extra == 'getAddress':
            sentMessage(chat_id, "Shifohonani xaritadan tanlab linkini tashlang: foydalanuvchiga oson bo'lishi uchun")
            doctor_uz.address = chooseLangUz(user, response)
            doctor_uz.save()
            doctor_ru.address = chooseLangRu(user, response)
            doctor_ru.save()
            user.status_extra = 'getAddress2'
            user.save()
        elif user.status_extra == 'getAddress2':
            sentMessage(chat_id, 'Klinikada qabul qilish vaqtini kiriting: misol uchun:\n'
                                 'Dushanba - Juma 10:30 - 15:30,\nShanba, Yakshanba Dam olish kuni ')
            doctor_uz.place_id = response['text']
            doctor_uz.save()
            doctor_ru.place_id = response['text']
            doctor_ru.save()
            user.status_extra = 'getTime'
            user.save()
        elif user.status_extra == 'getTime':
            sentMessage(chat_id, 'Mutaxasisligingiz nima?')
            doctor_uz.price_time = chooseLangUz(user, response)
            doctor_uz.save()
            doctor_ru.price_time = chooseLangRu(user, response)
            doctor_ru.save()
            user.status_extra = 'getProfession'
            user.save()
        elif user.status_extra == 'getProfession':
            sentMessage(chat_id, 'Diplom rasmi yoki hujjatini tashlang: ')
            doctor_uz.professions = makeWord(chooseLangUz(user, response))
            doctor_uz.save()
            doctor_ru.professions = makeWord(chooseLangRu(user, response))
            doctor_ru.save()
            user.status_extra = 'getDocument'
            user.save()
        elif user.status_extra == 'getDocument':
            sentMessage(chat_id, 'Diplom rasmi yoki hujjatini tashlang: ')
            # elif user.status_extra == 'getPassport':
            #     sentMessage(chat_id, 'Passport rasmini tashlang: ')
        elif user.status_extra == 'getPicture':
            sentMessage(chat_id, "Qidiruv natijasida chiqish uchun o'zingi rasmingizni rasmingizni tashlang: ")
        elif user.status_extra == 'getPrice':
            try:
                doctor_uz.price = response['text']
                doctor_uz.save()
                doctor_ru.price = response['text']
                doctor_ru.save()
                sentMessage(chat_id, "Uyga kelib ko'rish narxi qancha? ", ['inline_keyboard',
                                                                           [[["Uyga borib ko'rmiman.", 'no_price']]]])
                user.status_extra = 'getHomePrice'
                user.save()
            except:
                sentMessage(chat_id, "Bir martalik qabulingiz narxi qancha faqar raqamda va so'mda kiritng:")
        elif user.status_extra == 'getHomePrice':
            try:
                doctor_uz.home_price = chooseLangUz(user, response)
                doctor_uz.save()
                doctor_ru.home_price = chooseLangRu(user, response)
                doctor_ru.save()
                sentMessage(chat_id, "Tajribangiz nechi yil.")
                user.status_extra = 'getExperience'
                user.save()
            except:
                deleteMessage(chat_id, response['message_id'] - 1)
                sentMessage(chat_id, "Uyga kelib ko'rish narxi qancha? ", ['inline_keyboard',
                                                                           [[["Uyga borib ko'rmiman.", 'no_price']]]])

        elif user.status_extra == 'getExperience':
            sentMessage(chat_id, "Yana ma'lumot qo'shmoqchimisiz? Marhamat jo'nating",
                        ['inline_keyboard', [[["Yo'q qoshmiman", 'no_data']]]])
            doctor_uz.experience = chooseLangUz(user, response)
            doctor_uz.save()
            doctor_ru.experience = chooseLangRu(user, response)
            doctor_ru.save()
            user.status_extra = 'getOptional'
            user.save()
        elif user.status_extra == 'getOptional':
            sentMessage(chat_id, "Siz haqingizdagi ma'lumot adminga jo'natildi. Admin javobini kuting.")
            doctor_uz.optional = chooseLangUz(user, response)
            doctor_uz.save()
            doctor_ru.optional = chooseLangRu(user, response)
            doctor_ru.save()
            user.status = 'nothing'
            user.save()
            chat_id2 = sendNotification(user, doctor_uz, doctor_ru)
            sentMessage(chat_id2, "Doctor qo'shilsinmi?",
                        ['inline_keyboard', [[['yes', f'addDoctor_{doctor_uz.unique_id}'],
                                              ['no', f'noDoctor_{doctor_uz.unique_id}']]]])
    elif user.status_extra == 'getDocument':
        file_id = getFileId(response)
        user.status_extra = 'getPicture'
        user.save()
        if file_id:
            sentMessage(chat_id, "Qidiruv natijasida chiqish uchun o'zingi rasmingizni rasmingizni tashlang: ")
        else:
            sentMessage(chat_id, 'Diplom rasmi yoki hujjatini tashlang: ')
            user.status_extra = 'getDocument'
            user.save()
        doctor_uz.document_id = file_id
        doctor_uz.save()
        doctor_ru.document_id = file_id
        doctor_ru.save()
        # elif user.status_extra == 'getPassport':
        #     file_id = getFileId(response)
        #     user.status_extra = 'getPicture'
        #     user.save()
        #     if file_id:
        #         sentMessage(chat_id, "Qidiruv natijasida chiqish uchun o'zingi rasmingizni rasmingizni tashlang: ")
        #     else:
        #         sentMessage(chat_id, 'Passport rasmi yoki hujjatini tashlang: ')
        #         user.status_extra = 'getPassport'
        #         user.save()
        #     doctor_uz.document_picture_id = file_id
        #     doctor_uz.save()
        #     doctor_ru.document_picture_id = file_id
        #     doctor_ru.save()
    elif user.status_extra == 'getPicture':
        file_id = getFileId(response)
        user.status_extra = 'getPrice'
        user.save()
        if file_id[:5] == 'photo':
            sentMessage(chat_id, "Bir martalik qabulingiz narxi qancha faqar raqamda va so'mda kiritng: ")
        else:
            sentMessage(chat_id, "Qidiruv natijasida chiqish uchun o'zingi rasmingizni rasmingizni tashlang: ")
            user.status_extra = 'getPicture'
            user.save()
        doctor_uz.picture_id = file_id
        doctor_uz.save()
        doctor_ru.picture_id = file_id
        doctor_ru.save()


def chooseLangUz(user, response):
    """ if user language russian and return translated text into Uzbek"""

    if user.language == 0:
        return response['text']
    else:
        text = response['text']
        return translater_uz.translate(text)


def chooseLangRu(user, response):
    """ if user language uzbek and return translated text into russian """

    if user.language == 1:
        return response['text']
    else:
        text = response['text']
        return translater_ru.translate(text)


def sendMenu(user, message, chat_id, check, text=''):
    """ for create main menu and send to user """

    lang = user.language
    cq = ['inline_keyboard', [[[text_menu['cq_menu'][lang][0], 'search_med']],
                              [[text_menu['cq_menu'][lang][1], 'search_doc']],
                              [[text_menu['cq_menu'][lang][2], 'how']],
                              [[text_menu['cq_menu'][lang][3], 'change_lang']]
                              ]]
    if check:
        message_id = sentMessage(chat_id, text + text_menu['menu'][lang], cq)
        message_id = message_id['result']['message_id']
        user.callback_data = message_id
        user.save()
    else:
        message_id = editMessage(chat_id, user.callback_data, text + text_menu['menu'][lang], cq)


def sendSearchDoctor(user, message, chat_id, check):
    """ for create main menu and send to user """

    lang = user.language
    cq = ['inline_keyboard', [[[text_menu['search_menu'][lang][1][0], 'searchByName']],
                              [[text_menu['search_menu'][lang][1][1], 'searchByProfession']],
                              [[text_menu['search_menu'][lang][1][2], 'contact']],
                              [[text_menu['search_menu'][lang][1][3], 'exit']]
                              ]]
    if check:
        message_id = sentMessage(chat_id, text_menu['search_menu'][lang][0], cq)
        message_id = message_id['result']['message_id']
        user.callback_data = message_id
        user.save()
    else:
        message_id = editMessage(chat_id, user.callback_data, text_menu['search_menu'][lang][0], cq)


def selectCity(user, message, chat_id, check):
    """ for create main menu and send to user """

    lang = user.language
    cq = ['inline_keyboard', City(user)]

    if check:
        message_id = sentMessage(chat_id, text_menu['search_city'][lang], cq)
        message_id = message_id['result']['message_id']
        user.callback_data = message_id
        user.save()
    else:
        message_id = editMessage(chat_id, user.callback_data, text_menu['search_city'][lang], cq)


def selectProfession(user, message, chat_id, check, next_status):
    """ send message for selecting profession """

    city = user.status_extra
    if city == '0':
        doctors = Doctor.objects.filter(language=user.language, doctor_status=True)
    else:
        doctors = Doctor.objects.filter(city=city, language=user.language, doctor_status=True)
    doctorlar = []
    for doctor in doctors:
        if doctor not in doctorlar:
            doctorlar.append(doctor)
    professions = searchProfession(city, user, doctorlar)
    text = f"{text_menu['search_menu'][2][user.language]} | {int(user.next_status) + 1} dan - " \
           f"{user.next_to_status} gacha | {len(professions)} tadan"
    if len(professions) > user.next_to_status:
        professions = professions[user.next_status:user.next_to_status]
        if user.next_status == 0:
            professions.append([[text_menu['search_menu'][user.language][1][4], f'more_pro']])
        else:
            professions.append([[text_menu['search_menu'][user.language][1][5], f'previus_pro'],
                               [text_menu['search_menu'][user.language][1][6], f'next_pro']])
        user.next_status = user.next_to_status
        user.next_to_status = user.next_to_status + 5
        user.save()
    else:
        if user.next_status > 4:
            professions.append([[text_menu['search_menu'][user.language][1][5], f'previus_pro']])
        del professions[0:next_status]
        user.next_status = user.next_to_status
        user.next_to_status = user.next_to_status + 5
        user.save()

    professions.append([[text_menu['search_menu'][user.language][1][3], 'exit']])
    professions.append([[text_menu['search_menu'][user.language][1][7], 'exit_menu']])
    if check:
        message_id = sentMessage(chat_id, text, ['inline_keyboard', professions])
        message_id = message_id['result']['message_id']
        user.callback_data = message_id
        user.save()
    else:
        message_id = editMessage(chat_id, user.callback_data, text, ['inline_keyboard', professions])


def sendsearchByName(user, message, chat_id, check):
    """ search menu editMessage or sendMessage """

    lang = user.language
    cq = ['inline_keyboard', [[[text_menu['searchbyname'][lang][1], 'exit']]]]
    if check:
        message_id = sentMessage(chat_id, text_menu['searchbyname'][lang][0], cq)
        message_id = message_id['result']['message_id']
        user.callback_data = message_id
        user.save()
    else:
        message_id = editMessage(chat_id, user.callback_data, text_menu['searchbyname'][lang][0], cq)


def searchProfession(city, user, doctors):
    """ search doctor's profession """

    doctors_list = []
    doctor_list = []
    dont_repeat = []
    number = 0
    for doctor in doctors:
        professions = doctor.professions.split(', ')
        for profession in professions:
            if profession not in dont_repeat:
                doctor_list.append([profession, f'get_profession_{profession}'])
                number += 1
                dont_repeat.append(profession)
            if (number % 2 == 0 and doctor_list != []) or len(doctors) == 1:
                doctors_list.append(doctor_list)
                doctor_list = []
    doctors_list.append(doctor_list)
    return doctors_list


def searchByProfession(user, response, chat_id, check, profession, next_status):
    """ send doctor who is profession """

    city = user.status_extra
    true_doctor = []
    lang = user.language
    # print(city, profession, next_status)
    if city == '0':
        doctors = Doctor.objects.filter(professions__icontains=profession, doctor_status=True)
    else:
        doctors = Doctor.objects.filter(professions__icontains=profession, city=city, doctor_status=True)
    for doctor in doctors:
        if doctor not in true_doctor:
            true_doctor.append(doctor)
    if lang == 0:
        text = f"{text_menu['city'][lang][int(city)]} bo'yicha: {profession} | {int(user.next_status) + 1} dan - " \
           f"{user.next_to_status} gacha | {len(true_doctor)} tadan"
    else:
        text = f"по {text_menu['city'][lang][int(city)]}: {profession} | от {int(user.next_status) + 1} - " \
               f"до {user.next_to_status} | от {len(true_doctor)}"
    true_doctor = searchDoctorByName(true_doctor, user.status_extra, user, '')
    if len(true_doctor) > user.next_to_status:
        true_doctor = true_doctor[user.next_status:user.next_to_status]
        if user.next_status == 0:
            true_doctor.append([[text_menu['search_menu'][lang][1][4], f'more_doctor{profession}']])
        else:
            true_doctor.append([[text_menu['search_menu'][lang][1][5], f'previus_doctor{profession}'],
                                [text_menu['search_menu'][lang][1][6], f'next_doctor{profession}']])
        user.next_status = user.next_to_status
        user.next_to_status = user.next_to_status + 5
        user.save()
    else:
        if user.next_status > 4:
            true_doctor.append([[text_menu['search_menu'][lang][1][5], f'previus_doctor{profession}']])
        del true_doctor[0:next_status]
        user.next_status = user.next_to_status
        user.next_to_status = user.next_to_status + 5
        user.save()

    true_doctor.append([[text_menu['search_menu'][lang][1][3], 'exit']])
    true_doctor.append([[text_menu['search_menu'][lang][1][7], 'exit_menu']])
    if check:
        message_id = sentMessage(chat_id, text, ['inline_keyboard', true_doctor])
        message_id = message_id['result']['message_id']
        user.callback_data = message_id
        user.save()
    else:
        message_id = editMessage(chat_id, user.callback_data, text, ['inline_keyboard', true_doctor])


doctord = lambda name, lang, city: Doctor.objects.filter(name__icontains=name, language=lang, city=city, doctor_status=True)
doctorc = lambda name, lang: Doctor.objects.filter(name__icontains=name, language=lang, doctor_status=True)


def sendResponse(user, chat_id, response, text, check, next_status):
    """ send doctors list to user """

    lang = user.language
    city = user.status_extra
    true_doctor = []
    names = text.split()
    for name in names:
        if user.language == 1:
            if city == '0':
                doctors = doctorc(name, 1)
                if not doctors:
                    doctors = doctorc(t(name), 1)
            else:
                doctors = doctord(name, 1, city)
                if not doctors:
                    doctors = doctord(t(name), 1, city)
        else:
            if city == '0':
                doctors = doctorc(name, 0)
                if not doctors:
                    doctors = doctorc(t(name), 0)
            else:
                doctors = doctord(name, 0, city)
                if not doctors:
                    doctors = doctord(t(name), 0, city)
        for doctor in doctors:
            if doctor not in true_doctor:
                true_doctor.append(doctor)
    if lang == 0:
        text1 = f"{text_menu['city'][lang][int(city)]} bo'yicha: {text} | {int(user.next_status) + 1} dan - " \
           f"{user.next_to_status} gacha | {len(true_doctor)} tadan"
    else:
        text1 = f"по {text_menu['city'][lang][int(city)]}: {text} | от {int(user.next_status) + 1} - " \
               f"до {user.next_to_status} | от {len(true_doctor)}"
    doctors = searchDoctorByName(true_doctor, user.status_extra, user, '')
    doctors = searchName(user, doctors, next_status, text)
    if check:
        message_id = sentMessage(chat_id, text1, ['inline_keyboard', doctors])
        message_id = message_id['result']['message_id']
        user.callback_data = message_id
        user.save()
    else:
        message_id = editMessage(chat_id, user.callback_data, text1, ['inline_keyboard', doctors])


def searchName(user, doctors, next_status, text):
    """ send answer for searching name """

    if len(doctors) > user.next_to_status:
        doctors = doctors[user.next_status:user.next_to_status]
        if user.next_status == 0:
            doctors.append([[text_menu['search_menu'][user.language][1][4], f'more_{text}']])
        else:
            doctors.append([[text_menu['search_menu'][user.language][1][5], f'previus_{text}'],
                            [text_menu['search_menu'][user.language][1][6], f'next_{text}']])
        user.next_status = user.next_to_status
        user.next_to_status = user.next_to_status + 5
        user.save()
    else:
        if user.next_status > 4:
            doctors.append([[text_menu['search_menu'][user.language][1][5], f'previus_{text}']])
        del doctors[0:next_status]
        user.next_status = user.next_to_status
        user.next_to_status = user.next_to_status + 5
        user.save()

    doctors.append([[text_menu['search_menu'][user.language][1][3], 'exit']])

    return doctors


def City(user):
    """ make cities to inline_keyboard """

    lang = user.language
    if user.status != 'addDoctor':
        lis = [[[text_menu['city'][lang][0], 'set_city0']], [[text_menu['city'][lang][1], 'set_city1']]]
    else:
        lis = [[[text_menu['city'][lang][1], 'set_city1']]]
    son = 2
    for son1 in range(7):
        li = []
        for son2 in range(2):
            li.append([text_menu['city'][lang][son], f'set_city{son}'])
            son += 1

        lis.append(li)

    lis.append([[text_menu['city'][lang][16], 'set_city16']])
    if user.status == 'search_doc' or user.status == 'searchProfession':
        lis.append([[text_menu['search_menu'][user.language][1][3], 'exit']])
        lis.append([[text_menu['search_menu'][user.language][1][7], 'exit_menu']])

    return lis


def getFileId(response):
    """ get photo or document id """

    if 'document' in response:
        file_id = response['document']['file_id']
        file_id = f"document_{file_id}"
    elif 'photo' in response:
        file_id = response['photo'][1]['file_id']
        file_id = f"photo_{file_id}"
    else:
        file_id = ''

    return file_id


def sendNotification(user, doctor_uz, doctor_ru):
    admins = Admin.objects.all()
    for admin in admins:
        chat_id = admin.user_id
        sentMessage(chat_id, f"----------{user.first_name} {user.user_id} foydalanuvchi admin bo'lmoqchi-----------\n\n"
                             f"<b>F.I.SH:</b> {doctor_uz.name}\n"
                             f"<b>Telfon raqami:</b> {doctor_uz.tel_number}\n"
                             f"<b>Shifoxona nomi:</b> {doctor_uz.working_place}\n"
                             f"<b>Shifoxona qaysi tumanda joylashgani:</b> {text_menu['city'][0][int(doctor_uz.city)]}\n"
                             f"<b>Shifoxona to'liq Manzili:</b> {doctor_uz.address}\n"
                             f"<b>Xaritadan:</b> {doctor_uz.place_id}\n"
                             f"<b>Mutaxasisligi:</b> {doctor_uz.professions}\n"
                             f"<b>Klinikada qabul qilish vaqti:</b> {doctor_uz.price_time}\n"
                             f"<b>Birmartalik qabul narxi:</b> {doctor_uz.price}\n"
                             f"<b>Uyga kelib ko'rish narxi:</b> {doctor_uz.home_price}\n"
                             f"<b>Tajribasi:</b> {doctor_uz.experience}\n"
                             f"<b>Yana ma'lumot:</b> {doctor_uz.optional}.\n\n"
                             f"---------------Ruscha---------------\n\n"
                             f"<b>ФИО:</b> {doctor_ru.name}\n"
                             f"<b>Номер телефона:</b> {doctor_ru.tel_number}\n"
                             f"<b>Название больницы:</b> {doctor_ru.working_place}\n"
                             f"<b>В каком районе находится больница?:</b> {text_menu['city'][1][int(doctor_ru.city)]}\n"
                             f"<b>Полный адрес больницы:</b> {doctor_ru.address}\n"
                             f"<b>С карты:</b> {doctor_ru.place_id}\n"
                             f"<b>Специальность:</b> {doctor_ru.professions}\n"
                             f"<b>Время приема в клинике:</b> {doctor_ru.price_time}\n"
                             f"<b>Стоимость разового посещения:</b> {doctor_ru.price}\n"
                             f"<b>Цена выезда на дом:</b> {doctor_ru.home_price}\n"
                             f"<b>Опыт:</b> {doctor_ru.experience}\n"
                             f"<b>Дополнительная информация:</b> {doctor_ru.optional}.")
        file_id = doctor_uz.document_id
        if file_id[:5] == 'photo':
            sendPhoto(chat_id, 'Diplom', file_id[6:])
        else:
            sendDocument(chat_id, 'Diplom', file_id[9:])
        # file_id = doctor_uz.document_picture_id
        # if file_id[:5] == 'photo':
        #     sendPhoto(chat_id, 'Passport', file_id[6:])
        # else:
        #     sendDocument(chat_id, 'Passport', file_id[9:])
        file_id = doctor_uz.picture_id
        sendPhoto(chat_id, 'Rasm', file_id[6:])

        return chat_id


def text_translater(a, c):
    if c != 1:
        return a.name
    else:
        return t(a.name)


def searchDoctorByName(true_doctor, city, user, profession):
    """ search doctor according city and name """

    doctor_list = []

    if len(true_doctor) > 1:
        for d in true_doctor:
            if user.status != 'searchProfession':
                profession = d.professions.split(', ')
                profession = profession[0]
            name = d.name
            doctor_list.append([[f"{name[:25]}...    {profession}", f"get_name_{d.unique_id}"]])
    else:
        if true_doctor:
            doctor_list = [[[f"{true_doctor[0].name[:25]}...    {profession}",
                             f"get_name_{true_doctor[0].unique_id}"]]]

    return doctor_list


def sendDoctorByName(user, response, chat_id, check, user_id):
    """ send info about doctor to user by name """

    doctor = Doctor.objects.get(unique_id=user_id, language=user.language)
    cq = ['inline_keyboard', [[['Qabuliga yozilish: ', f'enroll{doctor.user_id}']], [['sharh', f'comment']],
          [[text_menu['search_menu'][user.language][1][3], 'name_exit'],
           [text_menu['search_menu'][user.language][1][7], 'name_exit_menu']]]]
    caption = f"{doctor.name}\n\n🏥 {doctor.working_place} - {doctor.address} <a href='{doctor.place_id}'>Xaritada</a>" \
              f"\n\n<b>Klinikada qabul qilish vaqti</b>:\n{doctor.price_time}\n" \
              f"Birinchi qabul narxi: {doctor.price}.\nUyga kelib ko'rish narxi: {doctor.home_price}\n\n" \
              f"<i>👨‍⚕Shifokor haqida to'liqroq:</i> \n{doctor.professions},\n" \
              f"Tajribasi: {doctor.experience}\n{doctor.optional}"
    message = sendPhoto(chat_id, caption, doctor.picture_id[6:], cq, 'HTML').json()
    # user.callback_data = message['result']['message_id']
    # user.save()


def set_csv(user, doctors):
    try:
        with open('doctors.csv', 'w', newline='') as csvfile:
            fieldnames = ['language', 'city', 'name', 'username', 'user_id', 'unique_id', 'tel_number', 'working_place',
                          'address', 'place_id', 'professions', 'document_id', 'document_picture_id', 'picture_id', 'price',
                          'price_time', 'home_price', 'experience', 'optional', 'review', 'doctor_status', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for doctor in doctors:
                writer.writerow({'language': doctor.language, 'city': doctor.city, 'name': doctor.name,
                                 'username': doctor.username, 'user_id': doctor.user_id, 'unique_id': doctor.unique_id,
                                 'tel_number': doctor.tel_number, 'working_place': doctor.working_place,
                                 'address': doctor.address, 'place_id': doctor.place_id, 'professions': doctor.professions,
                                 'document_id': doctor.document_id, 'document_picture_id': doctor.document_picture_id,
                                 'picture_id': doctor.picture_id, 'price': doctor.price, 'price_time': doctor.price_time,
                                 'home_price': doctor.home_price, 'experience': doctor.experience, 'optional': doctor.optional,
                                 'review': doctor.review, 'doctor_status': doctor.doctor_status, 'status': doctor.status})
        return True
    except:
        return False