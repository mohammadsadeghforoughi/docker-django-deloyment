from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render, redirect

from .forms import UserRegistrationForm
from .models import User
from django.contrib.auth.views import LoginView


# Create your views here.

class SignView(LoginView):
    template_name = 'blog/login.html'
    redirect_authenticated_user = '/'


def logout_view(request):
    logout(request)
    return redirect('posts_archive')


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            User.objects.create_user(username=username, password=password, first_name=first_name,
                                     last_name=last_name, email=email)

            return redirect('login')
        else:
            pass
        context = {'form': form}
    else:
        form = UserRegistrationForm()
        context = {'form': form}
    return render(request, 'blog/register.html', context=context)
