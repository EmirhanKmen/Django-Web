"""
Sahaflar Platformu — Accounts Views
Handles user authentication, registration, and profile management.
"""
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import PulseLoginForm, PulseRegistrationForm, ProfileUpdateForm

User = get_user_model()


class PulseLoginView(LoginView):
    """Custom login view with Sahaflar Platformu branding."""
    template_name = 'accounts/login.html'
    authentication_form = PulseLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.request.GET.get('next', '/dashboard/')

    def form_valid(self, form):
        """Update last activity on login."""
        response = super().form_valid(form)
        self.request.user.last_activity = timezone.now()
        self.request.user.save(update_fields=['last_activity'])
        messages.success(self.request, f'Hos geldin, {self.request.user.get_full_name() or self.request.user.username}!')
        return response


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = PulseRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Hesabiniz basariyla olusturuldu! Sahaflar Platformu ile hos geldiniz.')
            return redirect('dashboard:index')
    else:
        form = PulseRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'Guvenli cikis yapildi.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Display and update user profile."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz guncellendi.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
