# DJANGO IMPORTS
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
# git test
# MY IMPORTS
from trackr.preview import PartPreview
from trackr.forms import MyFormStep1, BasePartForm
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
#from trackr.views import viewPartTable, viewPartTypeTable, manu_detail
from trackr import views
from trackr.forms import MyFormStep0, MyFormStep1
from trackr import wizard
urlpatterns = patterns('',
    #url(r'^test/', include('trackr.urls')),
    #url(r'parts/', include('trackr.urls')),
    #url(r'partType/', include('trackr.urls')),
    url(r'index/$', views.index),
    url(r'^part/$', views.part_table),
    url(r'^type/$', views.part_type_table),
    url(r'manufacturer_details/(\d+)', views.manu_detail, name='manufacturer'),
    url(r'current_count/$', views.part_count),
    url(r'mass_check_in/$', views.mass_check_in),
    url(r'check_in/$', views.check_in_or_update_part),
    url(r'check_out/$', views.check_out_part),
    url(r'add_part_type/$', views.add_part_type),
    url(r'file_upload/$', views.file_upload),
    url(r'part_log/$', views.search_log),
    url(r'easy/$', views.easy_check_in),
    url(r'easy_mass/$', views.easy_mass_check_in),
    url(r'wizard/$', views.FormWizard.as_view([MyFormStep0,MyFormStep1])),
#    url(r'^post/$', PartPreview(MyFormStep1)),

    
    
    
    
    
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
