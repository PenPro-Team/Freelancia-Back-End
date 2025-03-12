from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from .serializers import ReviewSerializer
from rest_framework.decorators import api_view
from .models import Review
from freelancia_back_end.models import User
# Create your views here.

@api_view(['POST'])
def create_review(request):

    user=User.objects.get(id=request.data['user_reviewed'])
    total_stars=user.rate*user.total_user_rated
    
    if request.data['user_reviewed']==request.data['user_reviewr']:
        return JsonResponse({'message': 'You can not review yourself'}, status=status.HTTP_400_BAD_REQUEST)
    

    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        total_stars+=request.data['rate']
        user.total_user_rated+=1
        user.rate=total_stars/user.total_user_rated
        user.save()
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# reviews that the user has received elhasanat
@api_view(['GET'])
def get_reviews(request, user_id):
    reviews = Review.objects.filter(user_reviewed=user_id)
    
    if not reviews.exists():
        return JsonResponse(
            {'message': 'The user does not have any reviews'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ReviewSerializer(reviews, many=True)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

#  reviews that the user has made elsyeate

@api_view(['GET'])
def get_user_reviwes (request, user_id):
    reviews = Review.objects.filter(user_reviewr=user_id)
    
    if not reviews.exists():
        return JsonResponse(
            {'message': 'The user does not have any reviews'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ReviewSerializer(reviews, many=True)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_project_reviews(request,project_id):
    reviews=Review.objects.filter(project=project_id)
    if not reviews.exists():
        return JsonResponse({'message': 'The project does not have any reviews'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ReviewSerializer(reviews, many=True)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)



@api_view(['PUT','PATCH'])
def update_review(request,review_id):
    try:
        review=Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return JsonResponse({'message': 'The review does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    user=User.objects.get(id=request.data['user_reviewed'])
    total_stars=user.rate*user.total_user_rated
    
    # if review.user_reviewr !=request.user:
    #     print(review.user_reviewr)
    #     print(request.user)
    #     return JsonResponse({'message': 'You are not the owner of this review'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ReviewSerializer(instance=review, data=request.data, partial=True)
    if serializer.is_valid():
        total_stars-=review.rate
        total_stars+=request.data['rate']
        user.rate=total_stars/user.total_user_rated
        user.save()
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_review(request,review_id):
    review=Review.objects.get(id=review_id)
    user=User.objects.get(id=review.user_reviewed.id)
    total_stars=user.rate*user.total_user_rated
    total_stars-=review.rate
    user.total_user_rated-=1
    if user.total_user_rated==0:
        user.rate=0
    else:
        user.rate=total_stars/user.total_user_rated
    user.save
    # if review.user_reviewr != request.user:
    #     return JsonResponse({'message': 'You are not the owner of this review'}, status=status.HTTP_403_FORBIDDEN)
    review.delete()
    return JsonResponse({'message': 'Review was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

