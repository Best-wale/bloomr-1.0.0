
from . import views
from django.urls import path,include
from .views import RegisterView, LoginView, ProfileView,FarmViewSet, InvestmentViewSet, ROIRecordViewSet, WithdrawalViewSet
from rest_framework_simplejwt.views import TokenRefreshView

from rest_framework.routers import DefaultRouter
 

router = DefaultRouter()
router.register(r'api/farms', FarmViewSet,basename='farms')
router.register(r'farms', FarmViewSet, basename='farm')
router.register(r'investments', InvestmentViewSet, basename='investment')
router.register(r'rois', ROIRecordViewSet, basename='roi')
router.register(r'withdrawals', WithdrawalViewSet, basename='withdrawal')


urlpatterns = [
 
   #     pages
    path('',views.index, name='landing'),
    path('login/',views.user_login, name='login'),
    path('register/',views.user_register, name='register'),
    path('forgot_password/',views.forgot_password, name='forgot_password'),
    path('farmer-dashboard/',views.farmer_dashboard, name='farmer-dashboard'),
    path('investor-dashboard/',views.investor_dashboard, name='investor-dashboard'),
    path('investor-farm-detail/<int:farm_id>/',views.investor_farm_detail,name='investor-farm-detail'),

    #Api for the pages 

    path('api/register/', RegisterView.as_view(), name='register_api'),
    path('api/login/', LoginView.as_view(), name='login_api'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/me/', ProfileView.as_view(), name='profile'),

    # farms operations


  path('api/', include(router.urls)),
   #investment

]


