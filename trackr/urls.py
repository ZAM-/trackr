#from django.conf.urls import patterns, include, url
from django.conf.urls import patterns, include, url

from views import viewPartTable, viewPartTypeTable, manu_detail



# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^test/', include('trackr.urls')),
    #url(r'^$', viewPartTable),
    #url(r'^$', viewPartTypeTable),
    #url(r'^manu_detail/(\d+)', manu_detail, name='manu_detail'),
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
