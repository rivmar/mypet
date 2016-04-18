from django.contrib import admin

from .models import Species, Events, Pets

class SpeciesAdmin(admin.ModelAdmin):
	list_display = ('genus', 'species', 'suspecies')

admin.site.register (Species, SpeciesAdmin)

class PetsAdmin(admin.ModelAdmin):
	list_display = ('pet_name', 'u_name', 'species')

admin.site.register (Pets, PetsAdmin)
