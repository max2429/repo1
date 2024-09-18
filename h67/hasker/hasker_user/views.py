# -*- coding: utf-8 -*-
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView
from django.shortcuts import redirect

from .forms import LoginForm, UserSettingsForm, SignUpForm

User = get_user_model()


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'hasker_user/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            form.add_error('password', 'Incorrect password')
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('askme:index')


class CustomLogoutView(LogoutView):
    next_page = 'askme:index'


class CustomSettingsView(FormView):
    form_class = UserSettingsForm
    template_name = 'hasker_user/user_settings.html'
    success_url = reverse_lazy('askme:index')

    def get_form_kwargs(self):
        kwargs = super(CustomSettingsView, self).get_form_kwargs()
        if self.request.method == 'GET':
            kwargs.update({'initial': {
                'email': self.request.user.email,
            }})
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.email = form.cleaned_data['email']
        if form.cleaned_data['photo']:
            user.photo = form.cleaned_data['photo']
        user.save()
        return super(CustomSettingsView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('askme:index')
        return super(CustomSettingsView, self).dispatch(request, *args, **kwargs)


class CustomSignupView(FormView):
    form_class = SignUpForm
    template_name = 'hasker_user/signup.html'
    success_url = reverse_lazy('askme:index')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        photo = form.cleaned_data['photo']

        if User.objects.filter(username=username).exists():
            form.add_error('username', 'Username already exists')
            return self.form_invalid(form)
        if User.objects.filter(email=email).exists():
            form.add_error('email', 'Email already exists')
            return self.form_invalid(form)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            photo=photo
        )
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(self.request, user)

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        return super(CustomSignupView, self).form_invalid(form)
