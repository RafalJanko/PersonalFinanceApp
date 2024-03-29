import json
import threading

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from validate_email import validate_email

from .utils import token_generator

# Create your views here.


"""
Email threading class, created to speed up sending out emails by the app.
"""


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


"""
Email validation class for the login and registration views.
"""


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data["email"]

        if not validate_email(email):
            return JsonResponse({"email_error": "Email is invalid"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"email_error": "Sorry, email is in use. Please choose another one."},
                status=409,
            )
        return JsonResponse({"email_valid": True})


"""
Username validation for both login and registration views.
"""


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data["username"]

        if not str(username).isalnum():
            return JsonResponse(
                {
                    "username_error": "Username should contain only alphanumeric characters"
                },
                status=400,
            )
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {
                    "username_error": "Sorry, username is in use. Please choose another one."
                },
                status=409,
            )
        return JsonResponse({"username_valid": True})


"""
Simple registration view - saves users to DB
"""


class RegistrationView(View):
    def get(self, request):
        return render(request, "authentication/register.html")

    def post(self, request):
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        context = {"fieldValues": request.POST}

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "Password too short")
                    return render(
                        request, "authentication/register.html", context=context
                    )
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                email_subject = "Activate your account"
                current_site = get_current_site(request)
                email_body = {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": token_generator.make_token(user),
                }
                link = reverse(
                    "activate",
                    kwargs={"uidb64": email_body["uid"], "token": email_body["token"]},
                )
                activate_url = "http//" + current_site.domain + link

                email_body = (
                    "Hi "
                    + user.username
                    + "Please use thid link to verify your account\n"
                    + activate_url
                )
                email = EmailMessage(
                    email_subject,
                    email_body,
                    "noreply@personalfinanceapp.com",
                    [email],
                )
                EmailThread(email).start()
                messages.success(request, "User has been created successfully!")
                return render(request, "authentication/register.html")

        return render(request, "authentication/register.html")


"""
Class designed to check if user is already activated in DB through a sent email.
"""


class VerificationView(View):
    def get(self, request, uidb64, token):

        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect("login" + "?message=" + "User already activated")

            if user.is_active:
                return redirect("login")
            user.is_active = True
            user.save()
            messages.success(request, "Account activated successfully")
            return redirect("login")

        except Exception as e:
            pass

        return redirect("login")


"""
Login view.
"""


class LoginView(View):
    def get(self, request):
        return render(request, "authentication/login.html")

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(
                        request, "Welcome " + user.username + " You are now logged in"
                    )
                    return redirect("expenses")
                messages.error(
                    request,
                    "Account is not active. Please check your email to activate it.",
                )
                return render(request, "authentication/login.html")

            messages.error(request, "Invalid credentials. Please try again")
            return render(request, "authentication/login.html")

        messages.error(request, "Please fill all fields")
        return render(request, "authentication/login.html")


"""
Simple logout view.
"""

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, "You have been logged out!")
        return redirect("login")


"""
Class designed to send out an email to reset one's password.
"""


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, "authentication/reset-password.html")

    def post(self, request):
        email = request.POST["email"]
        context = {"values": request.POST}
        if not validate_email(email):
            messages.error(request, "Please supply a valid email")
            return render(request, "authentication/reset-password.html", context)
        current_site = get_current_site(request)
        user = User.objects.filter(email=email)

        if user.exists():
            email_contents = {
                "user": user[0],
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user[0].pk)),
                "token": PasswordResetTokenGenerator().make_token(user[0]),
            }
            link = reverse(
                "reset-user-password",
                kwargs={
                    "uidb64": email_contents["uid"],
                    "token": email_contents["token"],
                },
            )
            reset_url = "http//" + current_site.domain + link
            email_subject = "Password reset instructions"

            email = EmailMessage(
                email_subject,
                "Hi there, please cick the link below to reset the password.\n"
                + reset_url,
                "noreply@personalfinanceapp.com",
                [email],
            )
            EmailThread(email).start()
        messages.success(request, "We have sent you an email to reset your password")

        return render(request, "authentication/reset-password.html")


"""
Completing the Password reset function 
"""


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):

        context = {
            "uidb64": uidb64,
            "token": token,
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(
                    request, "Password link is invalid, please request a new one."
                )
                return render(request, "authentication/reset-password.html")

        except Exception as identifier:
            messages.info(request, "Something went wrong, try again.")
            return render(request, "authentication/set-new-password.html", context)

        return render(request, "authentication/set-new-password.html", context)

    def post(self, request, uidb64, token):
        context = {
            "uidb64": uidb64,
            "token": token,
        }
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "authentication/set-new-password.html", context)

        if len(password) < 6:
            messages.error(request, "Password needs to be at least 6 characters long")
            return render(request, "authentication/set-new-password.html", context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(
                request,
                "Password changed successfully. Please log in using your new password. ",
            )
            return redirect("login")
        except Exception as identifier:
            messages.info(request, "Something went wrong, try again.")
            return render(request, "authentication/set-new-password.html", context)
