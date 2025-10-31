from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator

# =====================================
# Custom User
# =====================================

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('investor', 'Investor'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    wallet_id = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    kyc_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)





    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def str(self):
        return f"{self.email} ({self.role})"


# =====================================
# Farm Model
# =====================================

class Farm(models.Model):
    CROP_CHOICES = [
        ("coffee", "Coffee"),
        ("maize", "Maize"),
        ("rice", "Rice"),
        ("wheat", "Wheat"),
        ("avocado", "Avocado"),
        ("tea", "Tea"),
        ("cocoa", "Cocoa"),
        ("other", "Other"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farms"
    )
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="farms/", blank=True, null=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Farm size in acres")
    crop_type = models.CharField(max_length=50, choices=CROP_CHOICES)
    location = models.CharField(max_length=255)
    valuation = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.TextField()

    # Tokenization + investment data
    token_id = models.CharField(max_length=50, blank=True, null=True)  # Hedera Token ID
    token_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('125.00'))
    investors = models.PositiveIntegerField(default=0)
    raised = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    expected_roi = models.FloatField(default=28.5)
    status = models.CharField(max_length=50, default='pending', help_text="pending, active, funded, completed")
    raised_in_cent = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def str(self):
        return f"{self.name} ({self.owner.email})"

    def save(self):
        if not self.valuation == 0:
            raised_in_cent = (self.raised/self.valuation)*100
        return raised_in_cent

# =====================================
# Investment Model
# =====================================
from django.db import models
from django.conf import settings

class Investment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('usd', 'USD'),
        ('hbar', 'HBAR'),
    ]

    investor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investments"
    )
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="investments"
    )
    tokens = models.PositiveIntegerField()
    invested = models.DecimalField(max_digits=15, decimal_places=2)
    currentValue = models.DecimalField(max_digits=15, decimal_places=2)
    roi = models.FloatField(default=28.5)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    transaction_hash = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'farm')

    def __str__(self):
        return f"{self.investor.email} → {self.farm.name}"
    




# ----------------------------------------------------
# 4️⃣ ROI Record
# ----------------------------------------------------
class ROIRecord(models.Model):
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name="roi_records")
    roi_amount = models.DecimalField(max_digits=15, decimal_places=2)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"ROI for {self.investment.investor.email} on {self.investment.farm.name}"


# ----------------------------------------------------
# 5️⃣ Withdrawal (Investor)
# ----------------------------------------------------
class Withdrawal(models.Model):
    METHOD_CHOICES = [("fiat", "Fiat"), ("crypto", "Crypto")]
    STATUS_CHOICES = [("pending", "Pending"), ("approved", "Approved"), ("completed", "Completed")]

    investor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    tx_hash = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.investor.email} - {self.amount} ({self.status})"
