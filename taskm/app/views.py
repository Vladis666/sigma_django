import json

from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User


def index(request):
    return render(request, "index.html")


def statistic(request):
    return render(request, "statistic.html")


def tasks(request):
    return render(request, "tasks.html")


def page_not_found(request, exception):
    return render(request, "notfound.html")


class LoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return JsonResponse({'error': 'Admin access required'}, status=403)
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)

        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'is_staff': user.is_staff
        })


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'id': user.id,
                'username': user.username,
                'is_staff': user.is_staff
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)


class LogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({'success': True})


class UserStatusView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse({
                'authenticated': True,
                'id': request.user.id,
                'username': request.user.username,
                'is_staff': request.user.is_staff
            })
        else:
            return JsonResponse({'authenticated': False})