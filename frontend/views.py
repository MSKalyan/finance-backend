from django.shortcuts import render, redirect
import requests

def get_base_url(request):
    return f"{request.scheme}://{request.get_host()}/api"



from users.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

def auth_required(view_func):
    def wrapper(request, *args, **kwargs):
        token = request.session.get("access")

        if not token:
            return redirect("login")

        try:
            AccessToken(token)
        except TokenError:
            request.session.flush()
            return redirect("login")

        user_id = request.session.get("user_id")
        if not user_id:
            return redirect("login")

        request.user = User.objects.get(id=user_id)  

        return view_func(request, *args, **kwargs)
    return wrapper


def home_view(request):
    if request.session.get("access"):
        return redirect("dashboard")
    return render(request, "frontend/home.html")



from users.serializers import RegisterSerializer

def register_view(request):
    if request.method == "POST":
        payload = {
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
            "role": request.POST.get("role"),
        }

        serializer = RegisterSerializer(data=payload)

        if serializer.is_valid():
            serializer.save()
            return redirect("login")

        return render(request, "frontend/register.html", {
            "error": serializer.errors
        })

    return render(request, "frontend/register.html")



from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)

            request.session["access"] = str(refresh.access_token)
            request.session["refresh"] = str(refresh)
            request.session["role"] = user.role
            request.session["user_id"] = user.id  

            return redirect("dashboard")

        return render(request, "frontend/login.html", {
            "error": "Invalid credentials"
        })

    return render(request, "frontend/login.html")


def logout_view(request):
    request.session.flush()
    return redirect("login")



def get_valid_access_token(request):
    access = request.session.get("access")

    try:
        AccessToken(access)
        return access
    except:
        request.session.flush()
        return None



from dashboard.views import SummaryView, CategoryBreakdownView, RecentActivityView, MonthlyTrendView
from rest_framework.test import APIRequestFactory

@auth_required
def dashboard_view(request):
    factory = APIRequestFactory()

    drf_request = factory.get("/")
    drf_request.user = request.user
    drf_request._force_auth_user = request.user  
    data = {}

    data["summary"] = SummaryView.as_view()(drf_request).data
    data["categories"] = CategoryBreakdownView.as_view()(drf_request).data
    data["recent"] = RecentActivityView.as_view()(drf_request).data
    data["trends"] = MonthlyTrendView.as_view()(drf_request).data

    return render(request, "frontend/dashboard.html", {"data": data})



from records.models import Record

@auth_required
def records_view(request):
    records = Record.objects.all().order_by("-date")

    return render(request, "frontend/records.html", {
        "records": records,
        "next_url": None,
        "prev_url": None,
    })



@auth_required
def create_record_view(request):
    if request.session.get("role") != "admin":
        return redirect("records")

    token = get_valid_access_token(request)
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        Record.objects.create(
            amount=request.POST.get("amount"),
            type=request.POST.get("type"),
            category=request.POST.get("category"),
            custom_category=request.POST.get("custom_category"),
            date=request.POST.get("date"),
            description=request.POST.get("description"),
            created_by=request.user
        )

        return redirect("records")

    return render(request, "frontend/record_form.html")



@auth_required
def edit_record_view(request, pk):
    if request.session.get("role") != "admin":
        return redirect("records")

    record = Record.objects.get(id=pk)

    if request.method == "POST":
        record.amount = request.POST.get("amount")
        record.type = request.POST.get("type")
        record.category = request.POST.get("category")
        record.custom_category = request.POST.get("custom_category")
        record.date = request.POST.get("date")
        record.description = request.POST.get("description")
        record.save()

        return redirect("records")

    return render(request, "frontend/record_form.html", {"record": record})


@auth_required
def delete_record_view(request, pk):
    if request.session.get("role") != "admin":
        return redirect("records")

    record = Record.objects.get(id=pk)
    record.delete()

    return redirect("records")