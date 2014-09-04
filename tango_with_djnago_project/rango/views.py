from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth import authenticate, login, logout
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from rango.bing_search import run_query
from django.contrib.auth.models import User

@login_required
def add_category(request):
    # Get the context from the request.
    context = RequestContext(request)
    category_list = get_category_list()

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
    return render_to_response('rango/add_category.html', {'form': form, 'category_list':category_list}, context)

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)
    category_list = get_category_list()

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)

            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html', {'category_list':category_list}, context)

            page.views = 0
            page.save()
            return category(request, category_name_url, {'category_list':category_list})
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response('rango/add_page.html',
            {'category_name_url':category_name_url,
            'category_name':category_name, 'form':form,
            'category_list':category_list},
            context)


def index(request):
  # Create a cookie  
  # request.session.set_test_cookie()  
    context = RequestContext(request)
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories':category_list}
  # print request.user
    for category in category_list:
        category.url = encode_url(category.name)

    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list

    category_list = get_category_list()    
    context_dict['category_list'] = category_list

    # ### NEW CODE ###
    # Obtaine our Response object early so we can add cookie information.
    response = render_to_response('rango/index.html', context_dict, context)
    
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtaine the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exists, we default to zero and cast that.
    visits = int(request.COOKIES.get('visits', '0'))

    # Does the cookie last_visit exist?
    if 'last_visit' in request.COOKIES:
        # Yes it does! Get the cookie's value.
        last_visit = request.COOKIES['last_visit']
        # Cast the value to a python date/time object.
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # If it's been more than a day since the last visit...
        if (datetime.now() - last_visit_time).days > 0:
            # ...reassign the value of the cookie to +1 of what it was before..
            response.set_cookie('visits', visits+1)
            # ...and update the last visit cookie , too.
            response.set_cookie('last_visit', datetime.now())
    else:
            # Cookie last_visit doesn't exist, so createit to the current date/time.
            response.set_cookie('last_visit', datetime.now())
    return response

def about(request):
    visit_count = int(request.COOKIES.get('visits', 0))
    context = RequestContext(request)
    category_list = get_category_list()  
    return render_to_response('rango/about.html', {'visit_count':visit_count, 'category_list':category_list}, context)

# def category_list(request):
#     context = RequestContext(request)
#     category_list = Category.objects.order_by('-likes')
#     context_dict = {'categories':category_list}
#     for category in category_list:
#         category.url = encode_url(category.name)
#     return render_to_response('rango/category_list.html', context_dict, context)


def get_category_list():
    category_list = Category.objects.all()
    for category in category_list:
        category.url = encode_url(category.name)
    return category_list

def page_list(request):
    context = RequestContext(request)
    page_list = Page.objects.all()
    context_dict = {'pages':page_list}
    return render_to_response('rango/page_list.html', context_dict, context)

def category(request, category_name_url):
    # Request our context
    context = RequestContext(request)

    # Change underscores in the category name to spaces.
    # URL's don't handle spaces well, so we encode them as underscores.
    category_name = decode_url(category_name_url)

    # Build up the dictionary we will use as out template context dictionary.
    context_dict = {'category_name': category_name, 'category_name_url': category_name_url}

    category_list = get_category_list()
    context_dict['category_list'] = category_list

    try:
        # Find the category with the given name.
        # Raises an exception if the category doesn't exist.
        # We also do a case insensitive match.
        category = Category.objects.get(name=category_name)
        context_dict['category'] = category
        # Retrieve all the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category).order_by('-views')

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        # We get here if the category does not exist.
        # Will trigger the template to display the 'no category' message.
        pass

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list

    # Go render the response and return it to the client.
    return render_to_response('rango/category.html', context_dict, context)

# Function to replace '_' with spaces in url's
def decode_url(category_name_url):
   category_name = category_name_url.replace('_', ' ')
   return category_name

def encode_url(category_name_url):
    category_name = category_name_url.replace(' ', '_')
    return category_name

def register(request):
    # if request.session.test_cookie_worked():
    #     print ">>> TEST COOKIE WORKED !"
    #     request.session.delete_test_cookie()
    # Like before, get the request's context.
    context = RequestContext(request)
    category_list = get_category_list()

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response(
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered, 'category_list':category_list},
            context)

def user_login(request):
    #Like before, obtaine the context for the user's request.
    context = RequestContext(request)
    category_list = get_category_list()

    # If the request is a HTTP POST, try to pull out the  relevat information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        # print user
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            #Is the account is active? It could have been disabled.
            if user.is_active:
                login(request, user)

                # If the account is valid and active, we can log the user in.
                # We'll send the user back to homepage.
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return render_to_response('rango/login.html', {'disabled_user':True, 'category_list':category_list}, context)
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            # return HttpResponseRedirect('', "Invalid login details supplied.")
            return render_to_response('rango/login.html', {'bad_details':True, 'category_list':category_list}, context)

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('rango/login.html', {'category_list':category_list}, context)

@login_required
def restricted(request):
    category_list = get_category_list()
    #context = RequestContext(request)
    return render(request, 'rango/restricted.html', {'category_list':category_list})

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take back the user to the homepage.
    return HttpResponseRedirect('/rango/')


def search(request):
    context = RequestContext(request)
    result_list = []
    category_list = get_category_list()

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render_to_response('rango/search.html', {'result_list': result_list,
                                                    'category_list':category_list}, context)
@login_required
def profile(request):
    context = RequestContext(request)
    category_list = get_category_list()
    context_dict = {'category_list':category_list}
    u = User.objects.get(username=request.user)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up= None

    context_dict['user'] = u
    context_dict['userprofile'] = up
    return render_to_response('rango/profile.html', context_dict, context)

def track_url(request):
    context = RequestContext(request)
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)

@login_required
def like_category(request):
    context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()
        return HttpResponse(likes)