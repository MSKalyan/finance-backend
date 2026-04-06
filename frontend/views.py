from django.shortcuts import render, redirect
import requests

def get_base_url(request):
    return f"{request.scheme}://{request.get_host()}/api"

def auth_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("access"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper
def home_view(request):
    if request.session.get("access"):
        return redirect("dashboard")
    return render(request, "frontend/home.html")
from users.serializers import RegisterSerializer  # ADD THIS

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
    refresh = request.session.get("refresh")

    headers = {"Authorization": f"Bearer {access}"}
    base_url = get_base_url(request)

    test = requests.get(f"{base_url}/dashboard/summary/", headers=headers)

    if test.status_code == 200:
        return access

    refresh_response = requests.post(
        f"{base_url}/refresh/",
        json={"refresh": refresh}
    )

    if refresh_response.status_code == 200:
        new_access = refresh_response.json().get("access")
        request.session["access"] = new_access
        return new_access

    request.session.flush()
    return None

@auth_required
def dashboard_view(request):
    token = get_valid_access_token(request)

    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}

    data = {}

    # Summary
    base_url = get_base_url(request)
    res = requests.get(f"{base_url}/dashboard/summary/", headers=headers)
    if res.status_code == 200:
        data["summary"] = res.json()

    # Category breakdown
    res = requests.get(f"{base_url}/dashboard/categories/", headers=headers)
    if res.status_code == 200:
        data["categories"] = res.json()

    # Recent activity
    res = requests.get(f"{base_url}/dashboard/recent/", headers=headers)
    if res.status_code == 200:
        data["recent"] = res.json()

    # Monthly trends
    res = requests.get(f"{base_url}/dashboard/trends/", headers=headers)
    if res.status_code == 200:
        data["trends"] = res.json()

    return render(request, "frontend/dashboard.html", {"data": data})

@auth_required
def records_view(request):
    token = get_valid_access_token(request)

    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}

    params = request.GET.dict()
    base_url= get_base_url(request)
    response = requests.get(
        f"{base_url}/records/",
        headers=headers,
        params=params
    )

    records = []
    next_url = None
    prev_url = None

    if response.status_code == 200:
        data = response.json()

        if isinstance(data, dict):  # paginated
            records = data.get("results", [])
            next_url = data.get("next")
            prev_url = data.get("previous")
        else:
            records = data

    return render(request, "frontend/records.html", {
        "records": records,
        "next_url": next_url,
        "prev_url": prev_url,
    })

@auth_required
def create_record_view(request):
    if request.session.get("role") != "admin":
        return redirect("records")

    token = get_valid_access_token(request)
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        payload = {
            "amount": request.POST.get("amount"),
            "type": request.POST.get("type"),
            "category": request.POST.get("category"),
            "custom_category": request.POST.get("custom_category"),
            "date": request.POST.get("date"),
            "description": request.POST.get("description"),
        }
        base_url = get_base_url(request)

        requests.post(f"{base_url}/records/", json=payload, headers=headers)
        return redirect("records")

    return render(request, "frontend/record_form.html")

@auth_required
def edit_record_view(request, pk):
    if request.session.get("role") != "admin":
        return redirect("records")

    token = get_valid_access_token(request)
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        payload = {
            "amount": request.POST.get("amount"),
            "type": request.POST.get("type"),
            "category": request.POST.get("category"),
            "custom_category": request.POST.get("custom_category"),
            "date": request.POST.get("date"),
            "description": request.POST.get("description"),
        }

        # remove empty values (important for PATCH)
        payload = {k: v for k, v in payload.items() if v}
        base_url = get_base_url(request)

        res = requests.patch(
            f"{base_url}/records/{pk}/",
            json=payload,
            headers=headers
        )

        print("PATCH STATUS:", res.status_code, res.text)

        return redirect("records")

    base_url = get_base_url(request)
    res = requests.get(f"{base_url}/records/{pk}/", headers=headers)
    record = res.json() if res.status_code == 200 else {}

    return render(request, "frontend/record_form.html", {"record": record})

@auth_required
def delete_record_view(request, pk):
    if request.session.get("role") != "admin":
        return redirect("records")

    token = get_valid_access_token(request)
    headers = {"Authorization": f"Bearer {token}"}
    base_url = get_base_url(request)

    requests.delete(f"{base_url}/records/{pk}/", headers=headers)

    return redirect("records")