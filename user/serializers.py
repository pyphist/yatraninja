from rest_framework import serializers

from user.models import Traveller


class TravellerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    first_name = serializers.StringRelatedField(source='user.first_name')
    last_name = serializers.StringRelatedField(source='user.last_name')
    age = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(source='user.last_login')

    def get_age(self, obj):
        return obj.get_age()

    class Meta:
        model = Traveller
        fields = (
            'id', 'user_id', 'first_name', 'last_name', 'mobile_number', 'gender', 'address', 'dob', 'age',
            'nationality',
            'profile_picture', 'verified', 'last_login')
