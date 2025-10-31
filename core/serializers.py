from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser,Farm,Investment, ROIRecord, Withdrawal



'''
class UserSerializer(serializers.ModelSerializer):

	class Meta:
		model = CustomUser
		fields = ['email','first_name','last_name','password']
		#password will not be seen in the serilizered data
		extra_kwarg = {'password' : {'write_only':True}}

	def create(self, validated_data):
		password = validated_data.pop('password',None)

		user = CustomUser.objects.create(**validated_data)

		if (password):
			user.set_password(password)
			user.save()
		return user
'''


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'password', 'password2', 'role', 'phone'
        ]

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user




class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the token (optional)
        token['email'] = user.email
        token['role'] = user.role
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add extra user info to response data
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
        }
        print(data)
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'role', 'kyc_status', 'wallet_id']




#farms 


from rest_framework import serializers
from .models import Farm

class FarmSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Farm
        fields = [
            "id",
            "owner",
            "owner_email",
            "name",
            "image",
            "size",
            "crop_type",
            "location",
            "valuation",
            "description",
            "token_id",      # New field
            "investors",     # New field
            "raised",        # New field
            "status",        # New field
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "owner_email",
            "created_at",
            "updated_at",
            'raised_in_cent',
        ]







class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = ['farm', 'tokens', 'invested', 'currentValue', 'roi', 'payment_method', 'transaction_hash']

    def validate_invested(self, value):
        if value <= 0:
            raise serializers.ValidationError("Investment amount must be greater than zero.")
        return value

    def create(self, validated_data):
        validated_data['investor'] = self.context['request'].user
        return super().create(validated_data)


class ROIRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ROIRecord
        fields = '__all__'


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = '__all__'
