from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.http.response import JsonResponse, HttpResponse
from django.db import connection
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

import random
import string
import json

from delivery.models import users, orders, deliveries
from delivery.serializers import UsersSerializer, DeliveriesSerializer, OrdersSerializer, ServiceSerializer

# Create your views here.
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        json_parser = JSONParser()
        signup_data = json_parser.parse(request)
        users_serializer = UsersSerializer(data=signup_data)
        # Creating Django User
        User.objects.create_user(username=signup_data.get('username'), password=signup_data.get('password'))
        #
        if users_serializer.is_valid():
            user = users_serializer.save()
            refresh = RefreshToken.for_user(user)
            return JsonResponse({"refresh": str(refresh), "access":str(refresh.access_token)}, safe=False)
        return JsonResponse(users_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

@csrf_exempt
def login(request):
    json_parser = JSONParser()
    login_data = json_parser.parse(request)
    username = login_data.get('username')
    password = login_data.get('password')
    # print(username, password)
    # user = authenticate(username=username, password=password)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM delivery_users WHERE username = %s', (username,))
    user = cursor.fetchone()
    # print(user)
    if user is not None:
        user_dict = {
            'id': user[0],
            'username': user[1],
            'fullname':user[2],
            'email': user[3],
            'password': user[4],
            'security_question_1': user[5],
            'answer_1': user[6],
            'security_question_2': user[7],
            'answer_2': user[8],
            'user_type': user[9],
            'register_date': user[10]
        }
        print(user_dict)
        django_user = authenticate(username=username, password=password)
        # print(django_user.password)
        # if check_password(password, django_user.password):
        if django_user:
            refresh = RefreshToken.for_user(django_user)
            request.session['jwt_access_token'] = str(refresh.access_token)
            request.session['jwt_refresh_token'] = str(refresh)
            request.session.set_expiry(0)
            return JsonResponse({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_type": user_dict['user_type']
            })
        else:
            return JsonResponse({"error": "Invalid User."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def logout(request):
    try:
        session = Session.objects.get(session_key=request.session.session_key)
        session.delete()
    except Session.DoesNotExist:
        pass
    return JsonResponse("LoggedOut", status=status.HTTP_204_NO_CONTENT)


# Helper View to generate a random password
def generate_password(length):
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    return password

@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        json_parser = JSONParser()
        reset_data = json_parser.parse(request)
        email = reset_data.get('email')

        # Check if the user exists in database
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM delivery_users WHERE email = %s', (email,))
        results = cursor.fetchall()

        if results is None:
            return JsonResponse('Error: User Not Found')
        
        # Generate a random password and update the user's password in the database
        password = generate_password(10)
        cursor.execute('UPDATE delivery_users SET password = %s WHERE email = %s', (password, email))
        connection.commit()

        subject = 'Password Reset Request'
        message = "To reset your password, please use the one time password: "+password+"\n\nIf you did not request a password reset, please ignore this email."
        from_email = 'sreekavya.shetty@gmail.com'
        recipient_list = [email]     # ['singh.shubhams1397@gmail.com']
        html_message = "<p>To reset your password, please use the one time password:</p><p>"+password+"</p><p>If you did not request a password reset, please ignore this email.</p>"
        sent = send_mail(subject, message, from_email, recipient_list, html_message=html_message)

        if sent:
            return JsonResponse("Mail Sent Successfully", safe=False)
        else:
            return JsonResponse("Failed to Send Mail", safe=False)


@csrf_exempt
def get_deliveries(request):
    # Get all deliveries where status != Delivered
    delivery_data = deliveries.objects.exclude(status = 'Delivered')
    delivery_serializer = DeliveriesSerializer(delivery_data, many = True)
    # delivery_json = JSONRenderer().render(delivery_serializer.data)

    return JsonResponse(delivery_serializer.data, safe = False)

         
@csrf_exempt
def place_order(request):
    json_parser = JSONParser()
    order_data = json_parser.parse(request)
    print(order_data)
    order_serializer = OrdersSerializer(data=order_data)
    if order_serializer.is_valid():
        order_serializer.save()
        print('Success')

        # delivery = {
        #     "trackingid":order_data.get('trackingid'),
        #     "driver":"Josh Sandler",
        #     "status":"Pending",
        #     "current_city":"Bloomington",
        #     "current_state":"Indiana",
        #     "latitude":39.795017,
        #     "longitude":-86.234566
        # }

        # delivery_data = json_parser.parse(delivery)
        # delivery_serializer = DeliveriesSerializer(data=delivery_data)
        # if delivery_serializer.is_valid():
        #     delivery_serializer.save()

        return JsonResponse("Order Placed Successfully", safe=False)
    return JsonResponse(order_serializer.errors, safe=False)

@csrf_exempt
def get_location(request):
    json_parser = JSONParser()
    tracking_data = json_parser.parse(request)
    trackingId = tracking_data.get('trackingId')

    # Check if the user exists in database
    cursor = connection.cursor()
    cursor.execute('SELECT latitude as lat, longitude as lng FROM delivery_deliveries WHERE trackingid = %s', (trackingId,))
    results = cursor.fetchall()
    # print(results)

    # Create a Dictionaryto capture latitude and longitude values
    location = {'lat': results[0][0], 'lng': results[0][1]} if results else None

    return JsonResponse(location, safe=False)

@csrf_exempt
def get_orders(request):
    # json_parser = JSONParser()
    # Check if the user exists in database
    cursor = connection.cursor()
    cursor.execute("SELECT o.source_address, o.source_address, TO_CHAR(o.orderdate, 'MM/DD/YYYY'), u.fullname, d.driver FROM delivery_orders o, delivery_users u, delivery_deliveries d  WHERE o.username = u.username and o.trackingid = d.trackingid")
    results = cursor.fetchall()

    connection.commit()

    orders = []
    
    for i in results:
        order = {
            "pickup": i[0],
            "destination": i[1],
            "cust_name": i[2],
            "order_date": i[3],
            "driver": i[4]
        }
        orders.append(order)
    # json_results = json.dumps(orders)
    # print(orders)

    return JsonResponse(orders, safe=False)

@csrf_exempt
def get_customers(request):

    user_data = users.objects.filter(user_type = 'Customer')
    user_serializer = UsersSerializer(user_data, many = True)
    # delivery_json = JSONRenderer().render(delivery_serializer.data)
    # print(user_serializer.data)
    return JsonResponse(user_serializer.data, safe = False)


@csrf_exempt
def add_service(request):
    json_parser = JSONParser()
    service_data = json_parser.parse(request)
    service_serializer = ServiceSerializer(data=service_data)
    if service_serializer.is_valid():
        service_serializer.save()
        return JsonResponse("Service Created Successfully", safe=False)
    return JsonResponse(service_serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

    
    






