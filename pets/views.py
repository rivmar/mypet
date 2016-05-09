from django.shortcuts import render, redirect, render_to_response
from django.utils.safestring import mark_safe
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

class GetObjectMixin():
	def get_object(self):
		object = super().get_object()
		if self.request.user == object.u_name:
			return object
		else:
			raise PermissionDenied

class PetFormMixin():
	'''Form validation at pet creation/update'''
	def form_valid(self, form):
		birth_date_ff = form.cleaned_data['form_birth_date']
		if birth_date_ff:
			birth_date_ff = birth_date_ff.split('.')[::-1]
		else:
			birth_date_ff = []
		pet_name_ff = form.cleaned_data['pet_name']
		instance = form.save(commit=False)
		instance.u_name = self.request.user
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

class PetsList(generic.ListView):
	model = Pets
	template_name = 'pets/petlist.html'
	context_object_name = 'pets'

	def get_queryset(self):
		pets = Pets.objects.filter(u_name=self.request.user)
		return pets

class PetDetailView(GetObjectMixin, generic.DetailView):
	model = Pets
	context_object_name = 'pet'
	template_name = 'pets/pet.html'

class PetAdd(PetFormMixin, generic.edit.CreateView):
	form_class = PetForm
	template_name = 'pets/pets_form.html'

class PetUpdate(PetFormMixin, GetObjectMixin, generic.edit.UpdateView):
	form_class = PetForm
	template_name = 'pets/pets_form.html'
	model = Pets

	def get_initial(self):
		initial = super(PetUpdate, self).get_initial()
		initial['form_birth_date'] = self.object.form_birth_date
		return initial

class EventAdd(GetObjectMixin, generic.edit.CreateView):
	form_class = EventForm
	model = Events
	template_name = 'pets/event_form.html'

	def get_initial(self):
		initial = super(EventAdd, self).get_initial()
		initial['event_date'] = datetime.date.today()
		return initial

	def get_context_data(self, **kwargs):
		context = super(EventAdd, self).get_context_data(**kwargs)
		pet = Pets.objects.get(id = self.kwargs['pk'])
		context['pet_name'] = pet
		return context

	def form_valid(self, form):
		instance = form.save(commit = False)
		instance.pet = Pets.objects.get(id = self.kwargs['pk'])
		instance.save()
		self.object = instance
		if self.object.event_type == 'D':
			pet = self.object.pet
			pet.is_dead = True
			pet.save()
		return redirect(self.get_success_url())

class  EventDetail(GetObjectMixin,generic.DetailView):
	model = Events
	context_object_name = 'event'
	template_name = 'pets/event.html'

class EventUpdate(GetObjectMixin, generic.edit.UpdateView):
	form_class = EventForm
	model = Events
	template_name = 'pets/event_form.html'

	def form_valid(self, form):
		instance = form.save()
		self.object = instance
		return redirect(self.get_success_url())

class EventDelete(GetObjectMixin,generic.edit.DeleteView):	
	model = Events
	template_name = 'pets/delete_event.html'

	def get_success_url(self):
		eventid = self.kwargs['pk']
		pet = Events.objects.get(pk = eventid).pet
		return '%s/petevents' % pet.get_absolute_url()

class EventsCalendar(HTMLCalendar):
    '''
    link: http://uggedal.com/journal/creating-a-flexible-monthly-calendar-in-django/
    '''
    def __init__(self, events):
        super(EventsCalendar, self).__init__()
        self.events = self.group_by_day(events)

    def formatday(self, day, weekday):

        green = '<img src="/static/images/g.png" />'
        yellow = '<img src="/static/images/y.png" />'
        orange = '<img src="/static/images/o.png" />'
        red = '<img src="/static/images/r.png" />'
        sred = '<img src="/static/images/sr.png" />'
        pink  = '<img src="/static/images/p.png" />' 
        viol = '<img src="/static/images/v.png" />'
        black = '<img src="/static/images/bl.png" />'
        grey = '<img src="/static/images/gr.png" />'
            	
        if day != 0:
        	cssclass = self.cssclasses[weekday]
        	if datetime.date.today() == datetime.date(self.year, self.month, day):
        		cssclass += ' today'
        	if day in self.events:
        		ev_types = set()
        		cssclass += ' filled'
        		for event in self.events[day]:
        			if event.event_type == 'F':
        				ev_types.add(green)
        			elif event.event_type == 'S':
        				ev_types.add(yellow)
        			elif event.event_type == 'FF' or event.event_type == 'RF' or event.event_type == 'SB':
        				ev_types.add(orange)
        			elif event.event_type == 'R' or event.event_type == 'HP':
        				ev_types.add(red)
        			elif event.event_type == 'HC':
        				ev_types.add(sred)
        			elif event.event_type == 'B':
        				ev_types.add(pink)
        			elif event.event_type == 'C' or event.event_type == 'L':
        				ev_types.add(viol)
        			elif event.event_type == 'D':
        				ev_types.add(black)	
        			else:
        				ev_types.add(grey)
        		return self.day_cell(cssclass, '<a href = "/%d/%02.d/%02.d">%d  %s</a>'% (self.year, self.month, day, day, ''.join(ev_types)))
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
  month = int(month)
  year = int(year)
  def find_last_next_month(year, month):
  	'''Find previous and next month'''
  	cur_date = datetime.date(year, month, 15)
  	step = datetime.timedelta(days=30)
  	next, prev = cur_date + step, cur_date - step
  	nmonth, nyear = '{:02}'.format(next.month), next.year
  	pmonth, pyear = '{:02}'.format(prev.month), prev.year
  	res = {'nmonth': nmonth, 'nyear': nyear, 'pmonth': pmonth, 'pyear': pyear}
  	return res 
  my_events = Events.objects.order_by('event_date').filter(
    event_date__year=year, event_date__month=month, pet__u_name=request.user
  )
  cal = EventsCalendar(my_events).formatmonth(year, month)
  flnm = find_last_next_month(year, month)
  flnm.update({'calendar': mark_safe(cal),'month': '{:02}'.format(month), 'year': year, 'user': request.user})
  return render_to_response('pets/cal_template.html', flnm)

class PetEventsView(GetObjectMixin, generic.ListView):
	model = Events
	template_name = 'pets/petevents.html'
	context_object_name = 'events'

	def get_context_data(self, **kwargs):
		context = super(PetEventsView, self).get_context_data(**kwargs)
		context['petid'] = self.kwargs['pk']
		context['petname'] = Pets.objects.get(id=self.kwargs['pk'])
		return context

	def get_queryset(self):
		list_of_events = Events.objects.filter(pet=self.kwargs['pk'])
		return list_of_events

class CalendarDay(generic.ListView):
	model = Events
	template_name = 'pets/calendarday.html'
	context_object_name = 'events'

	def get_queryset(self):
		day, month, year = map(int, (self.kwargs['day'], self.kwargs['month'], self.kwargs['year']))
		data = datetime.date(year, month, day)
		events = Events.objects.filter(pet__u_name = self.request.user, event_date = data)
		return events

class AddSpecies(generic.edit.CreateView):
	form_class = AddSpeciesForm
	template_name = 'pets/addspecies.html'
	success_url = '/newpet'

	def form_valid(self, form):
		instance = form.save()
		return redirect(self.success_url)

