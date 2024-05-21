from django.urls import path
from .views import Register,Login,ContactList,ConnectContact,MarkSpam,SearchByPhoneNumber,SearchByName


urlpatterns=[
	path('register/',Register.as_view(),name='register'),
	# path('contactList/',ContactList.as_view(),name='contactList'),

	path('login/',Login.as_view(),name='login'),
    path('allContacts/',ContactList.as_view(),name='allContacts'),
    path('connectContact/',ConnectContact.as_view(),name='connectContact'),
    path('markSpam/',MarkSpam.as_view(),name='markSpam'),
    path('searchByPhone/',SearchByPhoneNumber.as_view(),name='searchByPhoneNumber'),
    path('searchByName/', SearchByName.as_view(), name="searchByName"),
    

]