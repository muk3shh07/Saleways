from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    Category,
    Genre,
    ImageAlbum,
    Product,
    Size,
    Order,
    OrderItem,
    ShippingAddress,
    Review,
    Color,
    DiscountOffers,
)


class UserSerializer(serializers.ModelSerializer):
    # custom fields to be serialized.
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        # serialize only this field.
        fields = ["id", "_id", "username", "email", "name", "isAdmin"]

    # obj is User Instance
    def get__id(self, obj):
        return obj.id

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        name = obj.first_name
        if name == "":
            name = obj.email

        return name


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "_id",
            "username",
            "first_name",
            "email",
            "name",
            "isAdmin",
            "token",
        ]

    # generates token for the user
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

 