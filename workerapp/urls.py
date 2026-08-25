from django.conf.urls.static import  static
from workerpj import settings
from . import views
from django.urls import path

urlpatterns = [
    path('',views.login, name="login"),
    path('index/',views.index, name="index"),
    path('booking/',views.bookingf, name="pbooking"),
    path('profile/',views.profile, name="profile"),
    path('details/<str:worker>/<int:salary>/<str:worker_type>/<int:phone>', views.details, name='details'),
    path('mybookings/',views.mybookings, name="mybookings"),
    path('cancel/<int:id>/',views.cancel, name="cancel"),
    path('update/<int:id>/',views.update, name="update"),
    path('logout/',views.logout,name='logout'), 
    path('feedback/',views.fdback,name='feedback'),
    path("wfeedback/",views.wfeedback,name="wfeedback"),
    path('notification/',views.notify,name='notification'),
    path('construction/',views.construction, name="construction"), 
    path('RECONSTRUCTION/',views.RECONSTRUCTION, name="RECONSTRUCTION"), 
    path('ELECTRICAL/',views.ELECTRICAL, name="ELECTRICAL"), 
    path('review/',views.Review, name="review"), 
    path('seemore/',views.smore, name="seemore"), 
    path('creator/',views.creator, name="creator"), 
    path('registerworker/', views.registerWorker, name='registerworker'),
    path('registercustomer/', views.registerCustomer, name='registercustomer'),
    path('worker_dashboard/', views.worker_dashboard, name='worker_dashboard'),

   ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)