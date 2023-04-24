from rest_framework import serializers
from delivery.models import users, orders, deliveries, services
from django.contrib.auth.hashers import make_password

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ('username', 'fullname', 'email', 'password', 'security_question_1', 'answer_1', 'security_question_2', 
        'answer_2', 'user_type', 'register_date')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        hashed_password = make_password(password)

        user = users(
            username=validated_data['username'],
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            password=hashed_password,
            security_question_1=validated_data['security_question_1'],
            answer_1=validated_data['answer_1'],
            security_question_2=validated_data['security_question_2'],
            answer_2=validated_data['answer_2'],
            user_type=validated_data['user_type'],
            register_date=validated_data['register_date']
        )
        # user.set_password(validated_data['password'])
        user.save()
        return user

class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = orders
        fields = ('trackingid', 'username', 'orderdate', 'destination_address', 'source_address', 'delivery_service', 
        'package_weight')

class DeliveriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = deliveries
        fields = ('trackingid', 'driver', 'status', 'current_city', 'current_state', 'latitude', 'longitude')

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = services
        fields = ('name', 'package_size', 'price')