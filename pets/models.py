#coding: utf8

import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User


class Species(models.Model):
	genus = models.CharField('Род',max_length=20)
	species = models.CharField('Вид',max_length=20)
	suspecies = models.CharField('Подвид',max_length=20, blank=True)

	def __str__(self):
		sp_name = (self.genus, self.species, self.suspecies)
		return ' '.join(sp_name)

	class Meta(object):
		ordering = ['genus', 'species', 'suspecies']
		verbose_name = 'Вид'
		verbose_name_plural = 'Виды'
		unique_together = (('genus', 'species', 'suspecies'),)

class Pets(models.Model):
	Gen = (
		('0', 'Неизвестно'),
		('1', 'Самец'),
		('2', 'Самка'))
	u_name = models.ForeignKey(User)
	pet_name = models.CharField('Имя питомца', max_length=50)
	species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, 
		 verbose_name = 'Вид животного', related_name = 'keepers')
	morph = models.CharField('Морфа',max_length=50, blank = True)
	gender = models.CharField('Пол',max_length=1, choices = Gen)
	birth_date = models.IntegerField('Дата рождения',blank = True, null = True)
	birth_month = models.IntegerField('Месяц рождения',blank = True, null = True)
	birth_year = models.IntegerField('Год рождения',blank = True, null = True)
	fed_freq = models.IntegerField('Частота кормления', blank = True, null = True)
	pet_comment = models.TextField('Комментарий',blank = True)
	is_dead = models.BooleanField(default = False) #, editable = False)

	def __str__(self):
		return self.pet_name

	def get_absolute_url(self):
		return  '/%i' % self.id

	def form_birth_date(self):
		date_ar = []
		for i in (self.birth_date, self.birth_month, self.birth_year):
			if i:
				date_ar.append(i)
			else:
				date_ar.append(0)
		#return '.'.join(date_ar)
		return '{:02}.{:02}.{:04}'.format(*date_ar)

	def temp_birth_date(self):
		RU_MONTH_VALUES = {
    1:'январь',
    2:'февраль',
    3:'март',
    4:'апрель',
    5:'май',
    6:'июнь',
    7:'июль',
    8:'август',
    9:'сентябрь',
    10:'октябрь',
    11:'ноябрь',
    12:'декабрь'}

		date_ar = []
		if self.birth_date and self.birth_month and self.birth_year:
			return datetime.date(self.birth_year, self.birth_month, self.birth_date)
		elif self.birth_month and self.birth_year:
			return '%s %d г.' % (RU_MONTH_VALUES[datetime.date(self.birth_year, self.birth_month, 1).month], datetime.date(self.birth_year, self.birth_month, 1).year)
		elif self.birth_year:
			return '%d г.' % datetime.date(self.birth_year, 1, 1).year
		else:
			return None



	'''
	def calculate_age:
		if not species.birth_year: return 'Неизвестно'
		day = int(self.birth_date) if self.birth_date else 15
		month = int(self.birth_month) if self.birth_month else 6
		year = int(self.birth_year)
		birthday = datetime.date(year, month, day)
		today = datetime.date.today()
		return (today-birthday).days'''


	class Meta(object):
		ordering = ['pet_name']
		verbose_name = 'Питомец'
		verbose_name_plural = 'Питомцы'
		unique_together = (('u_name', 'pet_name'),)


class Events(models.Model):
	eventtype = (
		('F', 'Кормление'),
		('FF', 'Принудительное кормление'),
		('RF', 'Отказ от корма'),
		('R', 'Срыг'),
		('S', 'Линька'),
		('SB', 'Проблемная линька'),
		('HP', 'Проблемы со здоровьем'),
		('HC', 'Ветеринарные процедуры'),
		('B', 'Зимовка'),
		('C', 'Спаривание'),
		('L', 'Откладка яиц/роды'),
		('D', 'Смерть'),
		('O', 'Другое'))
	pet = models.ForeignKey(Pets)
	event_type = models.CharField('Событие', max_length=2, choices = eventtype, default = 'F')
	event_date = models.DateField('Дата')
	event_comment = models.TextField('Комментарий', blank = True)
	reminde_me = models.DateField('Напомнить мне', blank = True, null = True)
	reminder_comment = models.TextField('Текст напоминания', blank = True)

	def get_absolute_url(self):
		return '/event/%i' % self.id  

	class Meta(object):
		ordering = ['event_date']
		verbose_name = 'Event'
		verbose_name_plural = 'Events'

