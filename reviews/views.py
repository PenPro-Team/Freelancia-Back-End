
import decimal
from rest_framework import status
from .serializers import ReviewSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Review
from freelancia_back_end.models import User
from rest_framework.response import Response
# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def create_review(request):

    user_reviewer_id=request.data.get('user_reviewr')
    user_reviewed_id=request.data.get('user_reviewed')
    rate=request.data.get('rate')
    project_id=request.data.get('project')

    if user_reviewed_id is None or user_reviewer_id is None or rate is None or project_id is None:
        return Response({'message': 'Please provide all the required fields'}, status=status.HTTP_400_BAD_REQUEST)

    if request.data['user_reviewed']==request.data['user_reviewr']:
        return Response({'message': 'You can not review yourself'}, status=status.HTTP_400_BAD_REQUEST)
    
    user=User.objects.get(id=request.data['user_reviewed'])
    total_stars=user.rate*user.total_user_rated
    
    

    serializer = ReviewSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        total_stars+=decimal.Decimal(request.data['rate'])
        user.total_user_rated+=1
        user.rate=total_stars/user.total_user_rated
        user.save()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# reviews that the user has received elhasanat
@api_view(['GET'])
@permission_classes([AllowAny])
def get_reviews(request, user_id):
    reviews = Review.objects.filter(user_reviewed=user_id)
    
    if not reviews.exists():
        return Response(
            {'message': 'The user does not have any reviews'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ReviewSerializer(reviews, many=True, context={'request': request})
    return Response(serializer.data,status=status.HTTP_200_OK)

#  reviews that the user has made elsyeate
@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_reviwes (request, user_id):
    reviews = Review.objects.filter(user_reviewr=user_id)
    
    if not reviews.exists():
        return Response(
            {'message': 'The user does not have any reviews'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ReviewSerializer(reviews, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_project_reviews(request,project_id):
    reviews=Review.objects.filter(project=project_id)
    if not reviews.exists():
        return Response({'message': 'The project does not have any reviews'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ReviewSerializer(reviews, many=True, context={'request': request})
    return Response(serializer.data,  status=status.HTTP_200_OK)



@api_view(['PUT','PATCH'])
@permission_classes([IsAuthenticated])
def update_review(request,review_id):
    try:
        review=Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({'message': 'The review does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if review.user_reviewr != request.user :
        return Response({'message': 'You are not the owner of this review'}, status=status.HTTP_403_FORBIDDEN)
    user=User.objects.get(id=review.user_reviewed.id)
    total_stars=user.rate*user.total_user_rated
    new_rate=request.data.get('rate')
  
   
    if request.method == 'PATCH':
        serializer = ReviewSerializer(instance=review, data=request.data, partial=True, context={'request': request})
    else:
        serializer = ReviewSerializer(instance=review, data=request.data, context={'request': request})
    
    if serializer.is_valid():
        if  new_rate==None:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            total_stars-=review.rate
            total_stars+=new_rate
            if user.total_user_rated==0:
                user.rate=request.data['rate']
            else:
                user.rate=total_stars/user.total_user_rated
            user.save()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request,review_id):
    try:
        review=Review.objects.get(id=review_id)
        if review.user_reviewr!= request.user and request.user.role != 'admin':
            return Response({'message': 'You are not the owner of this review'}, status=status.HTTP_403_FORBIDDEN)
    except Review.DoesNotExist:
        return Response({'message': 'The review does not exist'}, status=status.HTTP_404_NOT_FOUND
)
    user=User.objects.get(id=review.user_reviewed.id)
    total_stars=user.rate*user.total_user_rated
    total_stars-=review.rate
    user.total_user_rated-=1
    if user.total_user_rated==0:
        user.rate=0
    else:
        user.rate=total_stars/user.total_user_rated
    user.save()
    review.delete()
    return Response({'message': 'Review was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

