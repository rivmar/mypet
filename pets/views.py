from django.shortcuts import render, redirect, render_to_response
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from django.http import HttpResponse

from calendar import HTMLCalendar
from itertools import groupby
import datetime

from django.utils.html import conditional_escape as esc

from pets.forms import PetForm, EventForm, AddSpeciesForm
from .models import Events, Pets

class PetsList(generic.ListView):
	model = Pets
	template_name = 'pets/petlist.html'
	context_object_name = 'pets'

	@method_decorator(login_required())
	def dispatch(self, request, *args, **kwargs):
		return super(PetsList, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		pets = Pets.objects.filter(u_name=self.request.user)
		return pets

class PetDetailView(generic.DetailView):
	model = Pets
	context_object_name = 'pet'
	template_name = 'pets/pet.html'

	def get_object(self):
		object = super(PetDetailView, self).get_object()
		if self.request.user == object.u_name and self.request.user.is_authenticated():
			return object
		else:
			raise PermissionDenied

class PetAdd(generic.edit.CreateView):
	form_class = PetForm
	template_name = 'pets/pets_form.html'

	def form_valid(self, form):
		birth_date_ff = form.cleaned_data['form_birth_date']
		if birth_date_ff:
			birth_date_ff = birth_date_ff.split('.')[::-1]
		else:
			birth_date_ff = []
		instance = form.save(commit=False)
		instance.u_name = self.request.user
		a = instance.pet_name
		data = []
		for k in range(3):
			try:
				data.append(birth_date_ff.pop(0))
			except IndexError:
				data.append(None)
		instance.birth_year, instance.birth_month, instance.birth_date = data
		if not instance.pet_name:
			psn = instance.species.__str__()
			uniq, i = False, 0
			while uniq == False:
				i+=1
				pr_pet_name = '%s %s' % (psn, i)
				if not Pets.objects.filter(u_name=self.request.user, pet_name=pr_pet_name).exists():
					instance.pet_name = pr_pet_name
					uniq = True
		instance.save()
		self.object = instance
		return redirect(self.get_success_url())

class PetUpdate(generic.edit.UpdateView):
	form_class = PetForm
	template_name = 'pets/pets_form.html'
	model = Pets

	def get_object(self):
		object = super(PetUpdate, self).get_object()
		if self.request.user == object.u_name and self.request.user.is_authenticated():
			return object
		else:
			raise PermissionDenied

	def get_initial(self):
		initial = super(PetUpdate, self).get_initial()
		initial['form_birth_date'] = self.object.form_birth_date
		return initial

	def form_valid(self, form):
		birth_date_ff = form.cleaned_data['form_birth_date']
		if birth_date_ff:
			birth_date_ff = birth_date_ff.split('.')[::-1]
		else:
			birth_date_ff = []
		pet_name_ff = form.cleaned_data['pet_name']
		instance = form.save(commit=False)
		data = []
		for k in range(3):
			try:
				data.append(birth_date_ff.pop(0))
			except IndexError:
				data.append(None)
		instance.birth_year, instance.birth_month, instance.birth_date = data
		if not pet_name_ff:
			psn = instance.species.__str__()
			uniq, i = False, 0
			while uniq == False:
				i+=1
				pr_pet_name = '%s %s' % (psn, i)
				if not Pets.objects.filter(u_name=self.request.user, pet_name=pr_pet_name).exists():
					instance.pet_name = pr_pet_name
					uniq = True
		instance.save()
		self.object = instance
		return redirect(self.get_success_url())

class EventAdd(generic.edit.CreateView):
	form_class = EventForm
	model = Events
	template_name = 'pets/event_form.html'

	def get_context_data(self, **kwargs):
		context = super(EventAdd, self).get_context_data(**kwargs)
		pet = Pets.objects.get(id = self.kwargs['pk'])
		context['pet_name'] = pet
		return context

	def get_object(self):
		object = super(EventAdd, self).get_object()
		if self.request.user == object.pet.u_name and self.request.user.is_authenticated():
			return object
		else:
			raise PermissionDenied

	def form_valid(self, form):
		instance = form.save(commit = False)
		instance.pet = Pets.objects.get(id = self.kwargs['pk'])
		instance.save()
		self.object = instance
		return redirect(self.get_success_url())

class  EventDetail(generic.DetailView):
	model = Events
	context_object_name = 'event'
	template_name = 'pets/event.html'

	def get_object(self):
		object = super(EventDetail, self).get_object()
		if self.request.user == object.pet.u_name and self.request.user.is_authenticated():
			return object
		else:
			raise PermissionDenied

class EventUpdate(generic.edit.UpdateView):
	form_class = EventForm
	model = Events
	template_name = 'pets/event_form.html'

	def get_object(self):
		object = super(EventUpdate, self).get_object()
		if self.request.user == object.pet.u_name and self.request.user.is_authenticated():
			return object
		else:
			raise PermissionDenied

	def form_valid(self, form):
		instance = form.save()
		self.object = instance
		return redirect(self.get_success_url())

class EventDelete(generic.edit.DeleteView):
	
	model = Events
	template_name = 'pets/delete_event.html'

	def get_success_url(self):
		eventid = self.kwargs['pk']
		pet = Events.objects.get(pk = eventid).pet
		return '%s/calendar' % pet.get_absolute_url()

	@method_decorator(login_required())
	def dispatch(self, request, *args, **kwargs):
		return super(EventDelete, self).dispatch(request, *args, **kwargs)

'''class Calendar(generic.ListView):

	def get(self, *args, **kwargs):
		self.date = datetime.date.today()
		cal = HTMLCalendar(0)
		response = HttpResponse(cal.formatyear(self.date.year))
		return response '''

class EventsCalendar(HTMLCalendar):

    def __init__(self, events):
        super(EventsCalendar, self).__init__()
        self.events = self.group_by_day(events)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if datetime.date.today() == datetime.date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.events:
                cssclass += ' filled'
                body = ['<ul>']
                for event in self.events[day]:
                    body.append('<li>')
                    body.append('<a href="%s">' % event.get_absolute_url())
                    body.append(esc(event.event_type))
                    body.append('</a></li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(EventsCalendar, self).formatmonth(year, month)

    def group_by_day(self, events):
        field = lambda event: event.event_date.day
        return dict(
            [(day, list(items)) for day, items in groupby(events, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)


def calendar(request, year=datetime.date.today().year, month=datetime.date.today().month):
  my_events = Events.objects.order_by('event_date').filter(
    event_date__year=year, event_date__month=month, pet__u_name=request.user
  )
  cal = EventsCalendar(my_events).formatmonth(year, month)
  return render_to_response('pets/cal_template.html', {'calendar': mark_safe(cal),})

class PetEventsView(generic.ListView):
	model = Events
	template_name = 'pets/petevents.html'
	context_object_name = 'events'

	@method_decorator(login_required())
	def dispatch(self, request, *args, **kwargs):
		return super(PetEventsView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(PetEventsView, self).get_context_data(**kwargs)
		context['petid'] = self.kwargs['pk']
		return context

	def get_queryset(self):
		list_of_events = Events.objects.filter(pet=self.kwargs['pk'])
		return list_of_events

class CalendarDay(generic.ListView):
	model = Events
	template_name = 'pets/calendarday.html'
	context_object_name = 'events'

	@method_decorator(login_required())
	def dispatch(self, request, *args, **kwargs):
		return super(PetsList, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		day, month, year = map(int, self.kwargs['day'], self.kwargs['month'], self.kwargs['year'])
		data = datetime.date(year, month, day)
		events = Events.objects.filter(pet__u_name = self.request.user, event_date = date)
		return events

class AddSpecies(generic.edit.CreateView):
	form_class = AddSpeciesForm
	template_name = 'pets/addspecies.html'
	success_url = '/newpet'

	def form_valid(self, form):
		instance = form.save()
		return redirect(self.success_url)

