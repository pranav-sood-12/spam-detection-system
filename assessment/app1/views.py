from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User_Profile,Contacts
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.hashers import make_password, check_password
from .serializers import ContactSerializer
import jwt 
from app1.models import User_Profile 
import jwt

# Create your views here.

class Register(APIView):
	def post(self,request):
		if request.data["username"] is None or request.data["phone_number"] is None:
			return Response(
				{
					"Error":"Both name and phone_number are required"
				}, 
				status = status.HTTP_400_BAD_REQUEST
			)
		try:
			if request.data["email"]:
				email = request.data["email"]
		except:
			email="NONE"
		hashed_password = make_password(request.data["password"])
		user_profile=User_Profile.objects.create(
	        		username=request.data["username"],
				    password=hashed_password,
	        		phone_number=request.data["phone_number"],
	        		email=email,
					spam=request.data["spam"]
	        	)
		if user_profile:

			user_profile.save()
			return Response(
	        	{
	        		"Message":"Registered successfully"
	        	},
	        	status = status.HTTP_200_OK
	        )
		else:
			return Response(
        		{
        			"Message":"Error during Signup!!"
        		},
        		status = status.HTTP_400_BAD_REQUEST
        	)


class Login(APIView):
	authentication_classes = [TokenAuthentication]
	def post(self, request):
		if not request.data:
			return Response(
            {"Error": "Please provide username/password"},
            status=status.HTTP_400_BAD_REQUEST
        )
		username = request.data.get("username")
		password = request.data.get("password")
		if username is None or password is None:
			return Response(
            {"Error": "Invalid Credentials"},
            status=status.HTTP_404_NOT_FOUND
        )
		try:
			user_profile = User_Profile.objects.get(username=username)
		except User_Profile.DoesNotExist:
			return Response(
            {"Error": "User does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )
		stored_password = user_profile.password
		phone_no = user_profile.phone_number
		if check_password(password, stored_password):
			jwt_payload = {'phone_no': phone_no}
			jwt_token = jwt.encode(jwt_payload, 'pranavsood', algorithm='HS256')
			response = Response({'message': 'success'},status=status.HTTP_200_OK)
			response.set_cookie('jwt_token', jwt_token, httponly=True)
			return response
		else:
			return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
		

class ContactList(APIView):
	def get(self,request):
		contacts=Contacts.objects.all()
		serializer=ContactSerializer(contacts,many=True)
		return Response(
			serializer.data
		)

class ConnectContact(APIView):	
	def post(self,request):
		name = request.data.get("name")
		phone_number = request.data.get("phone_number")
		email = request.data.get("email")
		spam = request.data.get("spam")
		
		if not (name and phone_number):
			return Response(
                {"Error": "Both name and phone_number are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
		token = request.COOKIES.get("jwt_token")
		print(token)
		
		if token:
			try:
				decoded_token = jwt.decode(token, 'pranavsood', algorithms=['HS256'])
				print(decoded_token)
				phone_number_from_token = decoded_token.get('phone_no')
				user_profile = User_Profile.objects.get(phone_number=phone_number_from_token)
				print(user_profile)
			except jwt.ExpiredSignatureError:
				return Response(
                    {"Error": "Token has expired"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
			except jwt.InvalidTokenError:
				return Response(
                    {"Error": "Invalid token"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
		else:
			return Response(
                {"Error": "Authentication credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED
            )
			
		contact = Contacts.objects.create(
            user_profile=user_profile,
            name=name,
            phone_number=phone_number,
            email=email,
			spam=spam
        )
		# print(contact)
		return Response(
            {"Message": "Contact saved successfully"},
            status=status.HTTP_201_CREATED
        )
	

class MarkSpam(APIView):
	def put(self,request):
		token = request.COOKIES.get("jwt_token")
		print(token)
		if not token:
			return Response(
                {"Error": "User not logged in"},
                status=status.HTTP_401_UNAUTHORIZED
            )
		
		phone_number=request.data.get("phone_number")
		if request.data["phone_number"] is None:
			return Response(
				{
					"Error":"Phone number required!!"
				},
				status = status.HTTP_400_BAD_REQUEST
			)
		contact=Contacts.objects.filter(phone_number=phone_number).update(spam=True)
		profile=User_Profile.objects.filter(phone_number=phone_number).update(spam=True)
		if (contact+profile):
			return Response(
				{
					"Message":"Contact marked as spam successfully!!"
				},
				status = status.HTTP_200_OK
			)
		else:
			return Response(
				{
					"Error":"Phone number not found!!"
				},
				status = status.HTTP_404_NOT_FOUND
			)
		
class SearchByPhoneNumber(APIView):
    def get(self, request):
        phone_number = request.data.get("phone_number")
        # print(phone_number)
        if not phone_number:
            return Response(
                {"Error": "Phone number required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profile = User_Profile.objects.get(phone_number=phone_number)

            return Response(
                {
                    "name": profile.username,
                    "phone_number": profile.phone_number,
                    "spam": profile.spam,
                    "email": profile.email
                },
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            try:

                contacts = Contacts.objects.filter(phone_number=phone_number)

                serializer = ContactSerializer(contacts,many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response(
                    {"Error": "No data found for the given phone number"},
                    status=status.HTTP_404_NOT_FOUND
                )

# class SearchByName(ListAPIView):
# 	queryset = Contacts.objects.all()
# 	serializer_class = ContactSerializer
# 	filter_backends = (SearchFilter,)
# 	search_fields = ('name','user_profile__username')

	# queryset = User_Profile.objects.all()
	# serializer_class = UserSerializer
	# filter_backends = (SearchFilter, OrderingFilter)
	# search_fields = ('username')
 

class SearchByName(APIView):
    def get(self, request):
        name = request.query_params.get("search")
        if name is None:
            return Response(
                {"Error": "Name is required!!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response = []

		
        user_profile_start = User_Profile.objects.filter(username__startswith=name)
        user_profile_contain = User_Profile.objects.filter(username__contains=name).exclude(username__startswith=name)
        contacts_start = Contacts.objects.filter(name__startswith=name)
        contacts_contain = Contacts.objects.filter(name__contains=name).exclude(name__startswith=name)


        for x in user_profile_start:
                response.append({
                    "name": x.username,
                    "phone_number": x.phone_number,
                    "spam": x.spam,
                })
				
        for y in contacts_start:
                response.append({
                    "name": y.name,
                    "phone_number": y.phone_number,
                    "spam": y.spam,
                })

        for x in user_profile_contain:
                response.append({
                    "name": x.username,
                    "phone_number": x.phone_number,
                    "spam": x.spam,
                })
				
        for y in contacts_contain:
                response.append({
                    "name": y.name,
                    "phone_number": y.phone_number,
                    "spam": y.spam,
                })

        return Response(response, status=status.HTTP_200_OK)
