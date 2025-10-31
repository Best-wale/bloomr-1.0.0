from django.shortcuts import render, redirect
from .serializers import UserSerializer
from rest_framework import generics, permissions, status,views,viewsets,permissions,mixins
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (RegisterSerializer, LoginSerializer, UserSerializer,FarmSerializer,InvestmentSerializer,ROIRecordSerializer,WithdrawalSerializer
)
from .models import CustomUser,Farm,Investment, ROIRecord, Withdrawal

def index(request):
	return render(request, "index.html",{})

def user_login(request):
	return render(request, "login.html",{})
	
def user_register(request):
	return render(request, "register.html",{})

def forgot_password(request):
	return render(request, "forgot-password.html",{})

def farmer_dashboard(request):

	return render(request, 'farmer-dashboard.html', {})
	
def investor_farm_detail(request,farm_id):
    farm = Farm.objects.get(pk=farm_id)
    #print(farm)
    return render(request,'investor-farm-detail.html',{'farm':farm})

def investor_dashboard(request):
	return render(request, 'investor-dashboard.html', {})


#api for app
#  Register
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Auto-generate tokens after registration
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


#  Login
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


# Get Current User
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

#Farm(get|post|delete|patch)
class FarmViewSet(viewsets.ModelViewSet):
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Allow guests to view

    def get_queryset(self):
        # If the user is authenticated, return only their farms; otherwise, return all farms
        if self.request.user.is_authenticated:
            return Farm.objects.filter(owner=self.request.user)
        return Farm.objects.all()  # Guest users can view all farms

    def perform_create(self, serializer):
        # Automatically assign the current user as the owner when creating a farm
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        # Ensure the user is trying to update their own farm
        farm = self.get_object()  # Get the farm instance being updated
        if farm.owner != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this farm.")
        serializer.save()  # Save the farm instance if the user is the owner


from rest_framework import viewsets, permissions





# INVESTMENT CRUD
from rest_framework import viewsets, permissions
from .models import Investment, Farm
from .serializers import InvestmentSerializer
from rest_framework.response import Response
from rest_framework import status

class InvestmentViewSet(viewsets.ModelViewSet):
    queryset = Investment.objects.all().order_by('-created_at')
    serializer_class = InvestmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        investor = self.request.user
        farm = serializer.validated_data['farm']
        invested_amount = serializer.validated_data['invested']

        # Check if the investment already exists
        investment, created = Investment.objects.get_or_create(
            investor=investor,
            farm=farm,
            defaults={'tokens': serializer.validated_data['tokens'], 'currentValue': serializer.validated_data['currentValue'], 'roi': serializer.validated_data['roi'], 'payment_method': serializer.validated_data['payment_method'], 'transaction_hash': serializer.validated_data['transaction_hash']}
        )

        if not created:
            # If it already exists, update the investment amount
            investment.invested += invested_amount
            farm.raised += invested_amount
            farm.save()
            investment.save()
        else:
            # If new investment, update the funds raised for the farm
            farm.funds_raised += invested_amount
            farm.save()

        return investment


# ROI RECORD VIEW
class ROIRecordViewSet(viewsets.ModelViewSet):
    queryset = ROIRecord.objects.all().order_by('-created_at')
    serializer_class = ROIRecordSerializer
    permission_classes = [permissions.IsAuthenticated]


# WITHDRAWAL VIEW
class WithdrawalViewSet(viewsets.ModelViewSet):
    queryset = Withdrawal.objects.all().order_by('-created_at')
    serializer_class = WithdrawalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(investor=self.request.user)

