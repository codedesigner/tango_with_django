from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
def index(request):
  context = RequestContext(request)
  context_dict = {'boldmessage': "i am bold font from context!!!"}
  return render_to_response('rango/index.html', context_dict, context)

def about(request):
  return HttpResponse("You are at rango's about page!!! <a href='/rango/'>Home</a>")
