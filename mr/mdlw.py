from django.template import RequestContext
from django.conf import settings
import re

from django.http import HttpResponseRedirect

class CheckUser():
	def __init__(self):
		self.exceptions = tuple(re.compile(url) for url in settings.LOGIN_URLS)

	def process_request(self, request):
		if request.user.is_authenticated():
			request_context = RequestContext(request)
			request_context.push({"user": request.user})
			return None
		for url in self.exceptions:
			if url.match(request.path):
				return None
		return HttpResponseRedirect('/auth/login/')

