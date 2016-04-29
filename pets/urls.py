from django.conf.urls import url
from . import views

urlpatterns = [
			url(r'^(?P<pk>[0-9]+)/$', views.PetDetailView.as_view(), name='petdetail'),
			url(r'^(?P<pk>[0-9]+)/newevent/$', views.EventAdd.as_view(), name='addevent'),
			url(r'^event/(?P<pk>[0-9]+)/$', views.EventDetail.as_view(), name='viewevent'),
			url(r'^event/(?P<pk>[0-9]+)/edit$', views.EventUpdate.as_view(), name='changeevent'),
			url(r'^event/(?P<pk>[0-9]+)/delete$', views.EventDelete.as_view(), name='deleteevent'),
			url(r'^(?P<pk>[0-9]+)/edit/$', views.PetUpdate.as_view(), name='changepet'),
			url(r'^(?P<pk>[0-9]+)/petevents/$', views.PetEventsView.as_view(), name='petevents'),
			url(r'^$', views.calendar, name='calendar'),
			url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.calendar, name='calendar'),
			url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$', views.CalendarDay.as_view(), name='day'),
			url(r'^newpet/$', views.PetAdd.as_view(), name='newpet'),
			url(r'^petlist/$',views.PetsList.as_view(), name='petlist'),
			url(r'^newspecies/$',views.AddSpecies.as_view(),  name='newspecies')
			]