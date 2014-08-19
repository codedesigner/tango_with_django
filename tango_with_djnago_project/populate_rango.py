import os

def populate():
  python_cat = add_cat("Python", views=128, likes=64)

  add_page(cat=python_cat,
        title="Official Python Tutorial",
        url="http://docs.python.org/2/tutorial/",
        views=128)

  add_page(cat=python_cat,
        title="How to Think like a computer Scientist",
        url="http://www.greenteapress.com/thinkpython/",
        views=110)

  add_page(cat=python_cat,
        title="Learn Pyhton in 10 minutes",
        url="http://www.korokithakis.net/tutorials/python/",
        views=98)

  django_cat = add_cat("Django", views=64, likes=32)

  add_page(cat=django_cat,
        title="Official Django Tutorial",
        url="http://docs.djangoproject.com/en/1.5/intro/tutorial01",
        views=130)

  add_page(cat=django_cat,
        title="Django Rocks",
        url="http://www.djangorocks.com/",
        views=44)

  add_page(cat=django_cat,
        title="How to Tango with Django",
        url="http://www.tangowithdjango.com/",
        views=80)

  frame_cat = add_cat("Other Frameworks", views=32, likes=16)

  add_page(cat=frame_cat,
        title="Bottle",
        url="http://bottleplay.org/docs/dev/",
        views=50)

  add_page(cat=frame_cat,
        title="Flask",
        url="http://flask.pocoo.org",
        views=50)

  fortran_cat = add_cat("Fortran", views=0, likes=0)

  add_page(cat=fortran_cat,
        title="Fortran",
        url="http://www.fortran.com/the-fortran-company-homepage/fortran-tutorials/",
        views=0)

  c_plus_plus_cat = add_cat("C++", views=0, likes=0)

  # Print out what we have added to user.
  for c in Category.objects.all():
    for p in Page.objects.filter(category=c):
      print "- {0} - {1}".format(str(c), str(p))

def add_page(cat, title, url, views=0):
  p, created = Page.objects.get_or_create(category=cat, title=title, url=url)
  p.views = views
  p.save()
  return p

def add_cat(name, views=0, likes=0):
  c, created = Category.objects.get_or_create(name=name)
  print Category.objects.get_or_create(name=name)
  print c
  print created
  c.views = views
  c.likes = likes
  c.save()
  return c

# Starts execution here!
if __name__ =='__main__':
  print "Starting Rango population script..."
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_djnago_project.settings')
  from rango.models import Category, Page
  populate()