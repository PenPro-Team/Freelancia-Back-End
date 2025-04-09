from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import ContactUs
from .serializers import ContactUsSerializer
from freelancia_back_end.pagination import BasePagination


class ContactUsAPIView(APIView):
    pagination_class = BasePagination
    serializer_class = ContactUsSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get(self, request):
        queryset = ContactUs.objects.all().order_by('-created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        try:
            contact = ContactUs.objects.get(id=id)
        except ContactUs.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(
            contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            contact = ContactUs.objects.get(id=id)
        except ContactUs.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        contact.delete()
        return Response(
            {"detail": "Deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
