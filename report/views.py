from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import ReportUser
from .serializers import ReportUserSerializer
from django.shortcuts import get_object_or_404
from freelancia_back_end.models import User
from rest_framework.pagination import PageNumberPagination
from freelancia_back_end.serializers import UserSerializer
from freelancia_back_end.pagination import PaginatedAPIView


class ReportUserAPIView(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            reports = ReportUser.objects.all()
            page = self.paginate_queryset(reports)
            if page is not None:
                serializer = ReportUserSerializer(
                    page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            serializer = ReportUserSerializer(
                reports, many=True, context={'request': request})
            return Response(serializer.data)
        return Response(
            {"detail": "You do not have permission to view all reports."},
            status=status.HTTP_403_FORBIDDEN
        )

    def post(self, request):
        reported_user = get_object_or_404(User, id=request.data.get('user'))

        serializer = ReportUserSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(
                reporter=request.user,
                user=reported_user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportUserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        report = get_object_or_404(ReportUser, id=report_id)
        if request.user == report.reporter or request.user == report.user or request.user.is_staff:
            serializer = ReportUserSerializer(report)
            return Response(serializer.data)
        return Response(
            {"detail": "You do not have permission to view this report."},
            status=status.HTTP_403_FORBIDDEN
        )

    def patch(self, request, report_id):
        report = get_object_or_404(ReportUser, id=report_id)
        if request.user.is_staff:
            serializer = ReportUserSerializer(
                report, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "You do not have permission to update this report."},
            status=status.HTTP_403_FORBIDDEN
        )

    def delete(self, request, report_id):
        report = get_object_or_404(ReportUser, id=report_id)
        if request.user.is_staff:
            report.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "You do not have permission to delete this report."},
            status=status.HTTP_403_FORBIDDEN
        )


class UserBanView(PaginatedAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        banned_users = User.objects.filter(is_active=False)

        search = request.GET.get('search', '').strip()
        if search:
            banned_users = banned_users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )

        page = self.paginate_queryset(banned_users)
        if page is not None:
            serializer = UserSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(
            banned_users, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.is_active = False
        user.save()

        return Response(
            {
                "detail": f"User {user.username} has been banned.",
                "user": UserSerializer(user, context={'request': request}).data
            },
            status=status.HTTP_200_OK
        )

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.is_active = True
        user.save()

        return Response(
            {
                "detail": f"User {user.username} has been unbanned.",
                "user": UserSerializer(user, context={'request': request}).data
            },
            status=status.HTTP_200_OK
        )
