from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Portfolio , PortfolioImage
from .serializers import PortfolioSerializer
from freelancia_back_end.permissions import IsOwnerOrAdminOrReadOnly

# Create your views here.
class PortfolioView(APIView):
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def get(self, request):
        portfolios = Portfolio.objects.all()

        user_id = request.query_params.get('user_id', None)
        if user_id:
            portfolios = portfolios.filter(user_id=user_id)

        serializer = PortfolioSerializer(portfolios, many=True , context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = PortfolioSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PortfolioAPI(APIView):
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def get(self, request, id):
        portfolio = get_object_or_404( Portfolio ,id=id)
        serializer = PortfolioSerializer(portfolio , context={'request': request})
        return Response(serializer.data)

    def put(self, request, id):
        portfolio = get_object_or_404( Portfolio ,id=id)
        self.check_object_permissions(request, portfolio)
        serializer = PortfolioSerializer(portfolio, data=request.data , context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, id):
        portfolio = get_object_or_404( Portfolio ,id=id)
        self.check_object_permissions(request, portfolio)
        serializer = PortfolioSerializer(portfolio, data=request.data , partial=True , context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        portfolio = get_object_or_404( Portfolio ,id=id)
        self.check_object_permissions(request, portfolio)
        portfolio.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)