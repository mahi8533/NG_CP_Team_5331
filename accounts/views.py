import json
from datetime import datetime
from urllib.parse import quote
from urllib.request import urlopen

from PIL import Image, UnidentifiedImageError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import CropRecord


def logout_view(request):
    logout(request)
    return redirect("login")


def login_view(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid email or password.")

    return render(request, "login.html")


def signup_view(request):
    if request.method == "POST":
        full_name = (request.POST.get("full_name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""
        confirm_password = request.POST.get("confirm_password") or ""

        if not full_name or not email:
            messages.error(request, "Please fill all required fields.")
            return render(request, "signup.html")
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "signup.html")
        if User.objects.filter(username=email).exists():
            messages.error(request, "Account with this email already exists.")
            return render(request, "signup.html")

        first_name = full_name.split(" ", 1)[0]
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            password=password,
        )
        user.save()
        messages.success(request, "Account created. Please log in.")
        return redirect("login")

    return render(request, "signup.html")


def forgot_password_view(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        new_password = request.POST.get("new_password") or ""
        confirm_password = request.POST.get("confirm_password") or ""

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "forgot_password.html")
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "forgot_password.html")

        user = User.objects.filter(username=email).first()
        if not user:
            messages.error(request, "No user found for this email.")
            return render(request, "forgot_password.html")

        user.set_password(new_password)
        user.save()
        messages.success(request, "Password reset successful. Please log in.")
        return redirect("login")

    return render(request, "forgot_password.html")


@login_required(login_url="login")
def dashboard(request):
    return render(request, "dashboard.html")


@login_required(login_url="login")
def crop(request):
    context = {}

    if request.method == "POST":
        location = (request.POST.get("location") or "").strip()
        season = request.POST.get("season") or ""
        soil_ph_raw = request.POST.get("soil_ph") or ""

        try:
            soil_ph = float(soil_ph_raw)
            if soil_ph < 0 or soil_ph > 14:
                raise ValueError
        except ValueError:
            context["error"] = "Please enter a valid soil pH between 0 and 14."
            return render(request, "crop.html", context)

        crop_map = {
            "Kharif": ["Rice", "Maize", "Soybean", "Groundnut"],
            "Rabi": ["Wheat", "Mustard", "Gram", "Barley"],
            "Zaid": ["Watermelon", "Cucumber", "Moong", "Sunflower"],
        }

        choices = crop_map.get(season, ["Wheat", "Rice", "Maize"])
        if soil_ph < 5.8:
            recommended = choices[0]
            reason = "Soil is slightly acidic."
        elif soil_ph <= 7.2:
            recommended = choices[1] if len(choices) > 1 else choices[0]
            reason = "Soil pH is in the healthy neutral range."
        else:
            recommended = choices[-1]
            reason = "Soil is alkaline."

        context["recommendation"] = {
            "crop": recommended,
            "location": location or "your area",
            "season": season,
            "soil_ph": soil_ph,
            "reason": reason,
        }

    return render(request, "crop.html", context)


@login_required(login_url="login")
def crop_records(request):
    if request.method == "POST":
        crop_name = (request.POST.get("crop_name") or "").strip()
        field_area_raw = request.POST.get("field_area_acres") or ""
        sowing_date_raw = request.POST.get("sowing_date") or ""
        expected_harvest_raw = request.POST.get("expected_harvest_date") or ""
        notes = (request.POST.get("notes") or "").strip()

        if not crop_name or not sowing_date_raw or not field_area_raw:
            messages.error(request, "Crop name, field area, and sowing date are required.")
            return redirect("crop_records")

        try:
            field_area = float(field_area_raw)
            if field_area <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Field area must be a positive number.")
            return redirect("crop_records")

        try:
            sowing_date = datetime.strptime(sowing_date_raw, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid sowing date.")
            return redirect("crop_records")

        expected_harvest_date = None
        if expected_harvest_raw:
            try:
                expected_harvest_date = datetime.strptime(expected_harvest_raw, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid expected harvest date.")
                return redirect("crop_records")

        CropRecord.objects.create(
            user=request.user,
            crop_name=crop_name,
            field_area_acres=field_area,
            sowing_date=sowing_date,
            expected_harvest_date=expected_harvest_date,
            notes=notes,
        )
        messages.success(request, "Crop record added successfully.")
        return redirect("crop_records")

    records = CropRecord.objects.filter(user=request.user)
    return render(request, "crop_records.html", {"records": records})


@login_required(login_url="login")
def delete_crop_record(request, record_id):
    if request.method == "POST":
        record = get_object_or_404(CropRecord, id=record_id, user=request.user)
        record.delete()
        messages.success(request, "Record deleted.")
    return redirect("crop_records")


def _get_json(url):
    with urlopen(url, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def _weather_text(code):
    code_map = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        51: "Light drizzle",
        61: "Light rain",
        63: "Moderate rain",
        65: "Heavy rain",
        80: "Rain showers",
        95: "Thunderstorm",
    }
    return code_map.get(code, "Variable conditions")


def _detect_soil_from_image(image_file):
    try:
        image = Image.open(image_file).convert("RGB")
    except UnidentifiedImageError:
        return None, "Could not read uploaded image."

    image = image.resize((120, 120))
    pixels = list(image.getdata())
    total = len(pixels)

    r_avg = sum(p[0] for p in pixels) / total
    g_avg = sum(p[1] for p in pixels) / total
    b_avg = sum(p[2] for p in pixels) / total
    brightness = (r_avg + g_avg + b_avg) / 3

    if brightness > 165 and abs(r_avg - g_avg) < 18 and abs(g_avg - b_avg) < 18:
        soil_type = "Sandy"
        confidence = 72
    elif r_avg > g_avg + 14 and r_avg > b_avg + 20:
        soil_type = "Clay"
        confidence = 70
    else:
        soil_type = "Loamy"
        confidence = 68

    return {
        "soil_type": soil_type,
        "confidence": confidence,
        "avg_rgb": (round(r_avg), round(g_avg), round(b_avg)),
    }, None


@login_required(login_url="login")
def weather(request):
    context = {}

    if request.method == "POST":
        location = (request.POST.get("location") or "").strip()
        if not location:
            context["error"] = "Please enter a location."
            return render(request, "weather.html", context)

        try:
            geo = _get_json(
                "https://geocoding-api.open-meteo.com/v1/search"
                f"?name={quote(location)}&count=1&language=en&format=json"
            )
            if not geo.get("results"):
                context["error"] = "Location not found. Try another city."
                return render(request, "weather.html", context)

            place = geo["results"][0]
            lat = place["latitude"]
            lon = place["longitude"]

            weather_data = _get_json(
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                "&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
                "&timezone=auto"
            )

            current = weather_data.get("current", {})
            context["weather_result"] = {
                "location": f"{place.get('name')}, {place.get('country')}",
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "precipitation": current.get("precipitation"),
                "wind": current.get("wind_speed_10m"),
                "summary": _weather_text(current.get("weather_code")),
            }
        except Exception:
            context["error"] = "Could not fetch weather right now. Please try again."

    return render(request, "weather.html", context)


@login_required(login_url="login")
def soil(request):
    context = {}

    if request.method == "POST":
        soil_type = (request.POST.get("soil_type") or "").strip()
        soil_ph_raw = request.POST.get("soil_ph") or ""
        soil_image = request.FILES.get("soil_image")

        detected = None
        if soil_image:
            detected, image_error = _detect_soil_from_image(soil_image)
            if image_error:
                context["error"] = image_error
                return render(request, "soil.html", context)
            context["detected_soil"] = detected

        if soil_type == "AUTO" and detected:
            soil_type = detected["soil_type"]
        elif soil_type == "AUTO":
            context["error"] = "Upload a soil image when using auto detect."
            return render(request, "soil.html", context)

        try:
            soil_ph = float(soil_ph_raw)
            if soil_ph < 0 or soil_ph > 14:
                raise ValueError
        except ValueError:
            context["error"] = "Enter a valid pH value between 0 and 14."
            return render(request, "soil.html", context)

        if soil_ph < 5.5:
            status = "Acidic"
            advice = "Apply agricultural lime and increase organic compost."
        elif soil_ph <= 7.5:
            status = "Balanced"
            advice = "Soil health is good. Continue balanced NPK and compost use."
        else:
            status = "Alkaline"
            advice = "Add gypsum and organic matter. Avoid excess sodium fertilizers."

        drainage = {
            "Sandy": "Fast drainage, frequent watering needed.",
            "Loamy": "Good drainage and nutrient retention.",
            "Clay": "Slow drainage, avoid over-irrigation.",
        }.get(soil_type, "Mixed behavior.")

        context["soil_report"] = {
            "soil_type": soil_type,
            "soil_ph": soil_ph,
            "status": status,
            "drainage": drainage,
            "advice": advice,
        }

    return render(request, "soil.html", context)
