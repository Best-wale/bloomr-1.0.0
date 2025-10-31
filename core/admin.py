
from django.contrib import admin
from .models import CustomUser, Farm, Investment,ROIRecord,Withdrawal

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'kyc_status', 'is_active', 'is_staff')
    list_filter = ('role', 'kyc_status', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'crop_type', 'valuation', 'status', 'expected_roi', 'created_at')
    list_filter = ('status', 'crop_type')
    search_fields = ('name', 'owner__email', 'location')
    ordering = ('-created_at',)


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('investor', 'farm', 'invested', 'tokens', 'payment_method', 'created_at')
    list_filter = ('payment_method', 'farm')
    search_fields = ('investoremail', 'farmname')
    ordering = ('-created_at',)

admin.site.register(ROIRecord)
admin.site.register(Withdrawal)