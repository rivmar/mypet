# coding: utf8

from django import forms
from django.core.exceptions import ValidationError
from .models import Pets, Events, Species
import re, datetime

class PetForm(forms.ModelForm):
	form_birth_date = forms.CharField (label = 'Дата рождения', max_length = 11, 
		required = False, help_text = '''В формате ГГГГ, ММ.ГГГГ или ДД.ММ.ГГГГ''')
	pet_name = forms.CharField(label = 'Имя питомца', required = False, help_text = '''Можно оставить поле пустым.
	 Имя будет сгенерировано из видового названия.''')
	class Meta(object):
		model = Pets
		fields = ('pet_name', 'species', 'morph', 'gender', 
			'form_birth_date', 'fed_freq', 'pet_comment')
		help_texts = {'fed_freq': 'Рекомендуемая частота кормлений. Будет использоваться для напоминаний о кормлении',
		'pet_comment': "Дополнительная информация, не включенная в другие поля"
		}

	def clean_form_birth_date(self):
		inp_data = self.cleaned_data['form_birth_date']
		error = ValidationError("Проверьте правильность ввода даты!")
		if not re.match('^(([0-9]{2}\.){,2}[0-9]{4})?$', inp_data):
			raise error
		if inp_data:
			data=inp_data.split('.')
			now = datetime.date.today()
			y = int(data.pop())
			if y<1950: raise error
			try:
				mm = int(data.pop())
				m = mm if mm!=0 else now.month
			except IndexError:
				m = now.month
			try:
				dd = int(data.pop())
				d = dd if dd!=0 else now.day
			except IndexError:
				d = now.day
			try:
				bd = datetime.date(y,m,d)
			except ValueError:
				raise error
			if bd > now:
				raise error
		return inp_data

class AddSpeciesForm(forms.ModelForm):
	class Meta(object):
		model = Species
		fields = '__all__'


class EventForm(forms.ModelForm):

	class Meta(object):
		model = Events
		exclude = ('pet',)
		help_texts = {'event_comment': 'Любые комментарии: тип и количество КО, поведение при кормлении и т.д.', 
		'reminde_me': 'Заполните это поле, если животное требует дополнительно обратить на себя внимание через\
		 некоторое время. Формат даты DD.MM.YYY', 'reminder_comment': 'Текст напоминания'}