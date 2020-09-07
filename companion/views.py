import datetime

from dateutil.tz import tz
from django.db.models import Q
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from companion.models import Request, Companion, Feedback
from companion.serializers import CompanionRequestSerializer, FeedbackListSerializer, CompanionSerializer
from companion.thread import NewCompanionRequestThread
from core.pagination import StandardResultsSetPagination
from user.models import Traveller


class RequestView(APIView):

    def post(self, request):
        traveller = Traveller.objects.get(user=self.request.user)
        request.data['request_owner_id'] = traveller.id
        serializer = CompanionRequestSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(request_owner=traveller)
            NewCompanionRequestThread(instance).start()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveRequestView(APIView):

    def delete(self, request, id):
        try:
            companion_request = Request.objects.get(pk=id)
            companion_request.delete()
            return Response({"success": True, "message": "Companion Request has been Deleted."})
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class FindRequestView(generics.ListAPIView):
    serializer_class = CompanionRequestSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        current_date = datetime.datetime.now(tz=tz.tzutc())
        previous_date = current_date - datetime.timedelta(7)

        # Filter last 24 hours request
        filters = Q(created_on__range=(previous_date, current_date)) & Q(status='ACTIVE') & Q(
            departure_date__gte=current_date)
        # Apply additional Filters
        if self.request.META.get('HTTP_TRIPTYPE'):
            trip_type = self.request.META.get('HTTP_TRIPTYPE')
            filters = filters & Q(trip_type=trip_type)
        if self.request.META.get('HTTP_ORIGINAIRPORT'):
            origin_airport = self.request.META.get('HTTP_ORIGINAIRPORT')
            filters = filters & Q(origin_airport=origin_airport)
        if self.request.META.get('HTTP_DESTINATIONAIRPORT'):
            destination_airport = self.request.META.get('HTTP_DESTINATIONAIRPORT')
            filters = filters & Q(destination_airport=destination_airport)
        if self.request.META.get('HTTP_DEPARTUREDATE'):
            departure_date = self.request.META.get('HTTP_DEPARTUREDATE')
            filters = filters & Q(departure_date=departure_date)
        if self.request.META.get('HTTP_DEPARTUREAIRLINES'):
            departure_airlines = self.request.META.get('HTTP_DEPARTUREAIRLINES')
            filters = filters & Q(departure_airlines=departure_airlines)
        if self.request.META.get('HTTP_RETURNAIRLINES'):
            return_airlines = self.request.META.get('HTTP_RETURNAIRLINES')
            filters = filters & Q(return_airlines=return_airlines)
        if self.request.META.get('HTTP_TRAVELLERTYPE'):
            traveler_type = self.request.META.get('HTTP_TRAVELLERTYPE')
            filters = filters & Q(traveler_type=traveler_type)
        if self.request.META.get('HTTP_SPONSORSHIP'):
            sponsorship = self.request.META.get('HTTP_SPONSORSHIP')
            filters = filters & Q(sponsorship=sponsorship)

        if filters is not None:
            filtered_request = Request.objects.filter(filters).exclude(request_owner__user=self.request.user).order_by(
                '-departure_date')

        return filtered_request

    def get_serializer_context(self):
        return {"user": self.request.user}


class RequestDetailView(APIView):

    def get(self, request, request_id):
        try:
            request = Request.objects.get(pk=request_id)
            return Response({"success": True, "request": request.get_request_details()})
        except:
            return Response({'success': False})


class CompanionView(generics.ListAPIView):
    serializer_class = CompanionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Companion.objects.filter(requestor__user=self.request.user).order_by('status')

    def post(self, request):
        try:
            companion_request = Request.objects.get(pk=request.data['request_id'])
            traveller = Traveller.objects.get(user=request.user)
            message = request.data['message']
            Companion.objects.create(request=companion_request, requestor=traveller, message=message)
            return Response({'success': True, 'message': 'Companion Request Created'})
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class CompletedView(generics.ListAPIView):
    serializer_class = CompanionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        current_date = datetime.datetime.now()
        return Companion.objects.filter(
            Q(requestor__user=self.request.user) & Q(status='ACCEPTED') & Q(
                request__departure_date__lt=current_date) & Q(
                request__trip_type='one-way') | Q(requestor__user=self.request.user) & Q(status='ACCEPTED') & Q(
                request__trip_type='round') & Q(
                request__return_date__lt=current_date)).order_by('-created_on')


class CompanionStatusView(APIView):

    def post(self, request):
        try:
            companion = Companion.objects.get(pk=request.data['companion_id'])
            status = request.data['status']
            if status:
                companion.status = status
                companion.save()
                return Response({'success': True, "status": status})
            else:
                return Response({'success': False, "massage": "Status is empty"})
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class CompanionRequestView(APIView):

    def get(self, request, request_id):
        try:
            request = Request.objects.get(pk=request_id)
            return Response({"success": True, "request": request.get_request_details(),
                             "companion": request.get_companions()})
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class RequestList(generics.ListAPIView):
    serializer_class = CompanionRequestSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        traveller = Traveller.objects.get(user=self.request.user)
        return Request.objects.filter(request_owner=traveller).order_by('-departure_date')


class FeedbackView(generics.ListAPIView):
    serializer_class = FeedbackListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        traveller = Traveller.objects.get(user=self.request.user)
        request_id_query_set = Request.objects.filter(request_owner=traveller).values('id')
        return Feedback.objects.filter(request__id__in=request_id_query_set).order_by('-review_date')

    def post(self, request):
        try:
            traveller = Traveller.objects.get(user=self.request.user)
            request_id = request.data.get('request_id', '')
            trip_request = Request.objects.get(pk=request_id)
            rating = request.data.get('rating', '')
            headline = request.data.get('headline', '')
            review = request.data.get('review', '')
            Feedback.objects.create(traveller=traveller, request=trip_request, rating=rating, headline=headline,
                                    review=review)
            return Response(
                {"success": True, "message": 'Feedback updated successfully'})
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)
