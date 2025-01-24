from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from Mbase.serializers import UserSerializer, UserSerializerWithToken

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # this function returns actual response to frontend.
    """
    refresh and access are returned under hood(Hover the pointer over TokenObtainPairSerializer and click on it for more details. )
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data

        """
        serializer: {'id': 1, '_id': 1, 'username': 'Sam', 'email': 'samirshahi9882@gmail.com', 'name': 'samirshahi9882@gmail.com', 'isAdmin': True, 
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjY0Nzg0MDEyLCJpYXQiOjE2NjIxOTIwMTIsImp0aSI6IjFhYzRhNjFjYTgwMzQwNGE4ZmUwNDIzZTM4YTEyNDY1IiwidXNlcl9pZCI6MX0.dnV2PalNENdhO8Iw3_RE2A4Ipq4gTRBELzfyXNuRMf8'}    
            
            """

        for key, value in serializer.items():
            data[key] = value
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

 
@api_view(["POST"])
def registerUser(request):
    data = request.data

    # Validate Emtyness
    required_fields = ["name", "email", "password"]
    for field in required_fields:
        if field not in data or not data[field]:
            return Response(
                {"detail": f"{field} is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    # Validate Password Length
    if len(data["password"]) < 8:
        return Response(
            {"detail": "Password must be at least 8 characters long"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Check if email already exists
        if User.objects.filter(email=data["email"]).exists():
            return Response(
                {"detail": "User with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create user
        user = User.objects.create(
            first_name=data["name"],
            username=data["email"],  # Username is set to email for simplicity
            email=data["email"],
            password=make_password(data["password"]),  # Hash the password
        )

        # Serialize user data with token
        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"detail": "An error occurred while creating the user", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    if request.method == "GET":
        # Get user profile data USING UserSerializer NO NEED TO USE UserSerializerWithToken
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    elif request.method == "PUT":
        # Update user profile data
        data = request.data
        # UserSerializerWithToken is used so only authenticated and owner can update it.
        serializer = UserSerializerWithToken(user, many=False)
        user.first_name = data["name"]
        user.username = data["email"]
        user.email = data["email"]
        user.save()
        # returning user details with token
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def listUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getUserDetails(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    user = User.objects.get(id=pk)

    data = request.data

    user.first_name = data["name"]
    user.username = data["email"]
    user.email = data["email"]
    user.is_staff = data["isAdmin"]

    user.save()

    serializer = UserSerializer(user, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def deleteUser(request, pk):
    userForDeletion = User.objects.get(id=pk)
    userForDeletion.delete()
    return Response("User was deleted")
