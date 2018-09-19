# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.urls import reverse

from users.forms import CustomUserCreationForm
from users.forms import CustomUserChangeProfileForm


User = get_user_model()


def signup(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display a blank registration form
        form = CustomUserCreationForm()
    else:
        # Process completed form
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            # log the user in then redirect to home page
            authenticated_user = authenticate(username=new_user.username, password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse_lazy('imageapp:index'))

    context = {'form': form}
    return render(request, 'users/signup.html', context)


@login_required
def password_change(request):
    """ Allows a user to change their own password."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(reverse('imageapp:profile', args=[request.user.username]))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    context = {
        'form': form,
    }
    return render(request, 'users/password_change.html', context)


@login_required
def edit_profile(request):
    """ View allows user to update their own settings."""
    if request.method == 'POST':
        form = CustomUserChangeProfileForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return HttpResponseRedirect(reverse('users:my_profile'))
    else:
        form = CustomUserChangeProfileForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'users/edit_profile.html', context)


@login_required
def my_profile(request):
    """ Displays the user's profile."""
    current_user = User.objects.get(username=request.user)
    context = {
        'current_user': current_user,
    }
    return render(request, 'users/my_profile.html', context)

