from rest_framework import serializers

class CategoryBreakdownSerializer(serializers.Serializer):
    category = serializers.CharField()
    total_income = serializers.FloatField()
    total_expense = serializers.FloatField()
    net_balance = serializers.FloatField()