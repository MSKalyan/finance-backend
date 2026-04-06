from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Case, When, FloatField
from django.db.models.functions import TruncMonth, Coalesce, Lower
from dashboard.serializers import CategoryBreakdownSerializer
from records.models import Record
from records.serializers import RecordSerializer
from users.permissions import DashboardPermission


def get_all_records():
    return Record.objects.all()


class SummaryView(APIView):
    permission_classes = [DashboardPermission]

    def get(self, request):
        records = get_all_records()

        income = records.filter(type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0

        expense = records.filter(type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0

        return Response({
            "total_income": income,
            "total_expense": expense,
            "net_balance": income - expense
        })

class CategoryBreakdownView(APIView):
    permission_classes = [DashboardPermission]

    def get(self, request):
        records = get_all_records()

        data = (
            records
            .annotate(
                final_category=Lower(
                    Coalesce('custom_category', 'category')
                )
            )
            .values('final_category')
            .annotate(
                total_income=Sum(
                    Case(
                        When(type='income', then='amount'),
                        default=0,
                        output_field=FloatField()
                    )
                ),
                total_expense=Sum(
                    Case(
                        When(type='expense', then='amount'),
                        default=0,
                        output_field=FloatField()
                    )
                )
            )
            .order_by('final_category')
        )

        result = []
        for item in data:
            result.append({
                "category": item["final_category"],
                "total_income": item["total_income"] or 0,
                "total_expense": item["total_expense"] or 0,
                "net_balance": (item["total_income"] or 0) - (item["total_expense"] or 0)
            })

        serializer = CategoryBreakdownSerializer(result, many=True)
        return Response(serializer.data)

class RecentActivityView(APIView):
    permission_classes = [DashboardPermission]

    def get(self, request):
        records = get_all_records().order_by('-date')[:5]
        serializer = RecordSerializer(records, many=True)
        return Response(serializer.data)


class MonthlyTrendView(APIView):
    permission_classes = [DashboardPermission]

    def get(self, request):
        records = get_all_records()

        data = (
            records
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(
                total_income=Sum(
                    Case(
                        When(type='income', then='amount'),
                        default=0,
                        output_field=FloatField()
                    )
                ),
                total_expense=Sum(
                    Case(
                        When(type='expense', then='amount'),
                        default=0,
                        output_field=FloatField()
                    )
                )
            )
            .order_by('month')
        )

        result = []
        for item in data:
            result.append({
                "month": item["month"].strftime("%Y-%m"),
                "total_income": item["total_income"] or 0,
                "total_expense": item["total_expense"] or 0,
                "net_balance": (item["total_income"] or 0) - (item["total_expense"] or 0)
            })

        return Response(result)