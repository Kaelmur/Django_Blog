from django.shortcuts import render, redirect
from datetime import datetime
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required, user_passes_test

year = datetime.now().year


@user_passes_test(lambda u: not u.is_authenticated, login_url='blog-home')
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Your account {username} has been created! Now you can Login.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {
        'form': form,
        'year': year
    })


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Your account has been updated!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'users/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'year': year
    })
