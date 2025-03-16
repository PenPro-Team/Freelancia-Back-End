from urllib.parse import urljoin
from rest_framework import serializers

from freelancia import settings
from .models import Portfolio, PortfolioImage

class PortfolioImageSerilaizer(serializers.ModelSerializer):
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            else:
                return urljoin(settings.MEDIA_URL, str(obj.image))
        return None
    class Meta:
        model = PortfolioImage
        fields = ['image']

class PortfolioSerializer(serializers.ModelSerializer):
    images = PortfolioImageSerilaizer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        print("Validated Data:", validated_data)
        images_data = self.context['request'].FILES.getlist('images')
        portfolio = Portfolio.objects.create(**validated_data)
        for image_data in images_data:
            PortfolioImage.objects.create(portfolio=portfolio, image=image_data)
        return portfolio

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        images_data = self.context['request'].FILES.getlist('images')
        internal_value['images'] = [{'image': image} for image in images_data]
        return internal_value

    class Meta:
        model = Portfolio
        fields = '__all__'
        read_only_fields = ['id' , 'user' , 'created_at' , 'updated_at']

    def create(self, validated_data):
        imgages_data = validated_data.pop('images')
        portfolio = Portfolio.objects.create(**validated_data)
        for image_data in imgages_data:
            PortfolioImage.objects.create(portfolio=portfolio , **image_data)
        return portfolio
