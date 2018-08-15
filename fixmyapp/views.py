from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Planning, PlanningSection, Profile
from .serializers import (
    PlanningSerializer, PlanningSectionSerializer, ProfileSerializer
)


class PlanningList(generics.ListAPIView):
    queryset = Planning.objects.all()
    serializer_class = PlanningSerializer


class PlanningDetail(generics.RetrieveAPIView):
    queryset = Planning.objects.all()
    serializer_class = PlanningSerializer


class PlanningSectionDetail(generics.RetrieveAPIView):
    queryset = PlanningSection.objects.all()
    serializer_class = PlanningSectionSerializer


@api_view(['PUT'])
def profile(request, profile_id):
    try:
        obj = Profile.objects.get(pk=profile_id)
        serializer = ProfileSerializer(obj, data=request.data)
        success_status = status.HTTP_200_OK
    except Profile.DoesNotExist:
        serializer = ProfileSerializer(data=request.data)
        success_status = status.HTTP_201_CREATED
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=success_status)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
