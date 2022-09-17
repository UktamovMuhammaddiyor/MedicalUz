from django.db import models


class Cities(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BotUser(models.Model):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255, default='')
    user_phone_number = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=255, default='/start')
    status_extra = models.CharField(max_length=255, default='/start')
    previs_status = models.CharField(max_length=255, default='')
    next_status = models.IntegerField(default=0)
    next_to_status = models.IntegerField(default=5)
    language = models.IntegerField(default='0')  # 0 for uz, 1 for ru
    callback_data = models.IntegerField(default=0)
    doctor_id = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.first_name


class Doctor(models.Model):
    language = models.CharField(max_length=255, default='')
    city = models.CharField(default='', max_length=255)
    name = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255, default='', blank=True)
    user_id = models.IntegerField(default=0, blank=True)
    unique_id = models.CharField(max_length=255, default='')
    tel_number = models.CharField(max_length=255, blank=True, default='')
    working_place = models.CharField(max_length=255, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    place_id = models.CharField(default='', max_length=255, blank=True)
    professions = models.CharField(max_length=255, blank=True, default='')
    document_id = models.CharField(max_length=255, blank=True, default='')
    document_picture_id = models.CharField(max_length=255, blank=True, default='')
    picture_id = models.CharField(max_length=255, blank=True, default='')
    price = models.IntegerField(default=0, blank=True)
    price_time = models.CharField(max_length=255, default='')
    home_price = models.CharField(max_length=255, default=0, blank=True)
    experience = models.CharField(max_length=255, default='', blank=True)
    optional = models.CharField(max_length=255, default='', blank=True)  # it is optional
    review = models.CharField(max_length=255, blank=True, default='')
    doctor_status = models.BooleanField(default='False', blank=True)
    status = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        return self.name


class Admin(models.Model):
    """ create a admin """

    user_id = models.IntegerField()
    username = models.CharField(max_length=255)

    def __str__(self):
        return self.username
# now don't need this
# class Address(models.Model):
#     name = models.CharField(max_length=255, blank=True)
#     city = models.ForeignKey(Cities, on_delete=models.CASCADE)
#     address = models.CharField(max_length=255)
#     phone_number = models.CharField(max_length=255)
#
#     def __str__(self):
#         return self.name
#
#
# class Medicines(models.Model):
#     address = models.ForeignKey(Address, on_delete=models.CASCADE)
#     medicine_name = models.CharField(max_length=255)
#     price = models.IntegerField()
#     manufacturer = models.CharField(max_length=255)
#
#     def __str__(self):
#         return self.medicine_name
#
