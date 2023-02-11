from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from validate_email import validate_email
from django.contrib import messages

# Create your views here.
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Sorry, email is in use. Please choose another one.'}, status=409)
        return JsonResponse({'email_valid':True})

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error':'Username should contain only alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Sorry, username is in use. Please choose another one.'}, status=409)
        return JsonResponse({'username_valid':True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        messages.success(request, "Account created successfully!")
        messages.warning(request, "Account created successfully!")
        messages.info(request, "Account created successfully!")
        messages.error(request, "Account created successfully!")
        return render(request, 'authentication/register.html')