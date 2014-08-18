from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from rango.models import Category, Page
from rango.forms import CategoryForm

def add_category(request):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('rango/add_category.html', {'form': form}, context)


def index(request):
  context = RequestContext(request)
  category_list = Category.objects.order_by('-likes')[:5]  
  page_list = Page.objects.order_by('-views')[:5]
  context_dict = {'categories':category_list, 'pages':page_list}
  for category in category_list:
    category.url = category.name.replace(' ', '_')
  return render_to_response('rango/index.html', context_dict, context)

def about(request):
  return render(request, 'rango/about.html')

def category(request, category_name_url):
  context = RequestContext(request)
  category_name = category_name_url.replace('_', ' ')
  context_dict = {'category_name' : category_name}
  try:
    category = Category.objects.get(name=category_name)
    pages = Page.objects.filter(category=category)
    context_dict['pages'] = pages
    context_dict['category'] = category
  except Category.DoesNotExist:
    pass

  return render_to_response('rango/category.html', context_dict, context)