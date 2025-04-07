from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.db import models
from .models import ReportUser, ReportContract
from .serializers import (
    ReportUserSerializer,
    ReportContractSerializer,
    CreateReportUserSerializer,
    CreateReportContractSerializer,
    UpdateUserReportStatusSerializer,
    UpdateContractReportStatusSerializer
)
from django.shortcuts import get_object_or_404
from freelancia_back_end.models import User
from contract.models import Contract
from rest_framework.pagination import PageNumberPagination
from freelancia_back_end.pagination import PaginatedAPIView
from freelancia_back_end.serializers import UserSerializer


class ReportUserAPIView(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            reports = ReportUser.objects.all().order_by('-created_at')
        else:
            reports = ReportUser.objects.filter(
                models.Q(reporter=request.user) |
                models.Q(user=request.user)
            ).order_by('-created_at')

        page = self.paginate_queryset(reports)
        if page is not None:
            serializer = ReportUserSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ReportUserSerializer(
            reports, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateReportUserSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportUserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, report_id):
        report = get_object_or_404(ReportUser, id=report_id)
        if (request.user == report.reporter or
            request.user == report.user or
                request.user.is_staff):
            return report
        raise PermissionDenied(
            "You don't have permission to access this report")

    def get(self, request, report_id):
        report = self.get_object(request, report_id)
        serializer = ReportUserSerializer(report)
        return Response(serializer.data)

    def patch(self, request, report_id):
        report = self.get_object(request, report_id)
        if request.user.is_staff:
            serializer = UpdateUserReportStatusSerializer(
                report,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        raise PermissionDenied("Only staff can update report status")

    def delete(self, request, report_id):
        report = self.get_object(request, report_id)
        if request.user.is_staff:
            report.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise PermissionDenied("Only staff can delete reports")


class ReportContractAPIView(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            reports = ReportContract.objects.all().order_by('-created_at')
        else:
            reports = ReportContract.objects.filter(
                reporter=request.user
            ).order_by('-created_at')

        page = self.paginate_queryset(reports)
        if page is not None:
            serializer = ReportContractSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ReportContractSerializer(
            reports, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateReportContractSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportContractDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, report_id):
        report = get_object_or_404(ReportContract, id=report_id)
        if (request.user == report.reporter or
                request.user.is_staff):
            return report
        raise PermissionDenied(
            "You don't have permission to access this report")

    def get(self, request, report_id):
        report = self.get_object(request, report_id)
        serializer = ReportContractSerializer(report)
        return Response(serializer.data)

    def patch(self, request, report_id):
        report = self.get_object(request, report_id)
        if request.user.is_staff:
            serializer = UpdateContractReportStatusSerializer(
                report,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        raise PermissionDenied("Only staff can update report status")

    def delete(self, request, report_id):
        report = self.get_object(request, report_id)
        if request.user.is_staff:
            report.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise PermissionDenied("Only staff can delete reports")


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
