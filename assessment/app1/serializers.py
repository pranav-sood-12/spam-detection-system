from rest_framework import serializers
from .models import Contacts,User_Profile

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Profile
        fields = '__all__'