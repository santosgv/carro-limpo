from django.contrib import auth
from django.shortcuts import redirect


def sair(request):
    auth.logout(request)
    return redirect('/accounts/login/')