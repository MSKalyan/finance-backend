from datetime import date
from rest_framework import serializers
from .models import Record

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = '__all__'
        read_only_fields =['created_by']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    def validate_type(self, value):
        if value not in ['income', 'expense']:
            raise serializers.ValidationError("Invalid type")
        return value
    
    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Date cannot be in the future")

        if value.year < 2000:
            raise serializers.ValidationError("Year must be >= 2000")

        return value
    
    def validate(self, data):
        category = data.get('category')
        custom_category = data.get('custom_category')

        if category == 'other':
            if not custom_category:
                raise serializers.ValidationError(
                    "custom_category is required when category is 'other'"
                )
            data['custom_category'] = custom_category.lower().strip()
        else:
            data['category'] = category.lower().strip()
            data['custom_category'] = None

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.category == 'other':
            data['category'] = instance.custom_category

        return data