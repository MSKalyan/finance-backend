from django.shortcuts import render, redirect
import requests
BASE_URL = "http://127.0.0.1:8000/api"
def auth_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("access"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper

def register_view(request):
    if request.method == "POST":
        payload = {
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
            "role": request.POST.get("role"),
        }

        response = requests.post(f"{BASE_URL}/register/", json=payload)

        if response.status_code == 201:
            return redirect("login")

        try:
            error_message = response.json()
        except:
            error_message = response.text or "Registration failed"

        return render(request, "frontend/register.html", {
            "error": error_message
        })

    return render(request, "frontend/register.html")

def login_view(request):
    if request.method == "POST":
        payload = {
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
        }

        response = requests.post(f"{BASE_URL}/login/", json=payload)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        if response.status_code == 200:
            try:
                tokens = response.json()
            except Exception:
                return render(request, "frontend/login.html", {
                    "error": "Invalid server response"
                })

            access = tokens.get("access")
            refresh = tokens.get("refresh")
            role=tokens.get("role")
            if access and refresh:
                request.session["access"] = access
                request.session["refresh"] = refresh
                request.session["role"] = role

                return redirect("dashboard")   # MUST exit here

            # if tokens missing → treat as failure
            return render(request, "frontend/login.html", {
                "error": "Login failed (tokens missing)"
            })

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
    test = requests.get(f"{BASE_URL}/dashboard/summary/", headers=headers)

    if test.status_code == 200:
        return access

    refresh_response = requests.post(
        f"{BASE_URL}/refresh/",
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
    res = requests.get(f"{BASE_URL}/dashboard/summary/", headers=headers)
    if res.status_code == 200:
        data["summary"] = res.json()

    # Category breakdown
    res = requests.get(f"{BASE_URL}/dashboard/categories/", headers=headers)
    if res.status_code == 200:
        data["categories"] = res.json()

    # Recent activity
    res = requests.get(f"{BASE_URL}/dashboard/recent/", headers=headers)
    if res.status_code == 200:
        data["recent"] = res.json()

    # Monthly trends
    res = requests.get(f"{BASE_URL}/dashboard/trends/", headers=headers)
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

    response = requests.get(
        f"{BASE_URL}/records/",
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

        requests.post(f"{BASE_URL}/records/", json=payload, headers=headers)
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

        res = requests.patch(
            f"{BASE_URL}/records/{pk}/",
            json=payload,
            headers=headers
        )

        print("PATCH STATUS:", res.status_code, res.text)

        return redirect("records")

    res = requests.get(f"{BASE_URL}/records/{pk}/", headers=headers)
    record = res.json() if res.status_code == 200 else {}

    return render(request, "frontend/record_form.html", {"record": record})

@auth_required
def delete_record_view(request, pk):
    if request.session.get("role") != "admin":
        return redirect("records")

    token = get_valid_access_token(request)
    headers = {"Authorization": f"Bearer {token}"}

    requests.delete(f"{BASE_URL}/records/{pk}/", headers=headers)

    return redirect("records")