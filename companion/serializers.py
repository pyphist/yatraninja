from rest_framework import serializers

from companion.models import Request, Feedback, Companion
from user.serializers import TravellerSerializer


class CompanionRequestSerializer(serializers.ModelSerializer):
    traveller = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_traveller(self, obj):
        serializer = TravellerSerializer(obj.request_owner)
        return serializer.data

    def get_status(self, obj):
        status = ''
        try:
            user = self.context.get("user")
            if user:
                status = Companion.objects.get(request=obj, requestor__user=user).status
        except:
            pass
        return status

    class Meta:
        model = Request
        fields = ('id', 'traveller', 'trip_type', 'origin_airport', 'destination_airport', 'departure_date',
                  'departure_airlines', 'return_date', 'return_airlines', 'adults', 'traveler_type', 'sponsorship',
                  'sponsorship_desc', 'status')
        extra_kwargs = {'request_owner': {'required': False}, 'return_date': {'required': False},
                        'return_airlines': {'required': False}, 'sponsorship_desc': {'required': False},
                        'status': {'required': False}, 'return_date': {'required': False},
                        'traveller': {'required': False}, 'status': {'required': False}}


class RequestSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    def get_owner(self, obj):
        serializer = TravellerSerializer(obj.request_owner)
        return serializer.data

    class Meta:
        model = Request
        fields = ('id', 'trip_type', 'origin_airport', 'destination_airport', 'departure_date',
                  'departure_airlines', 'return_airlines', 'adults', 'traveler_type', 'sponsorship',
                  'sponsorship_desc', 'owner')


class FeedbackListSerializer(serializers.ModelSerializer):
    traveller = serializers.SerializerMethodField()
    request = serializers.SerializerMethodField()

    def get_traveller(self, obj):
        serializer = TravellerSerializer(obj.traveller)
        return serializer.data

    def get_request(self, obj):
        serializer = CompanionRequestSerializer(obj.request)
        return serializer.data

    class Meta:
        model = Feedback
        fields = ('id', 'rating', 'headline', 'review', 'review_date', 'traveller', 'request')


class CompanionSerializer(serializers.ModelSerializer):
    request = serializers.SerializerMethodField()
    requestor = serializers.SerializerMethodField()

    def get_request(self, obj):
        serializer = RequestSerializer(obj.request)
        return serializer.data

    def get_requestor(self, obj):
        serializer = TravellerSerializer(obj.requestor)
        return serializer.data

    class Meta:
        model = Companion
        fields = ('id', 'request', 'requestor', 'message', 'status', 'created_on')
