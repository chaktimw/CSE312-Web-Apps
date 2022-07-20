from django.shortcuts import render, redirect
from django.contrib.auth import logout, decorators
from .forms import registerForm, profileUpdateForm, profileSigForm
from main.views import users


def register(request):
	if request.method == 'POST':
		form = registerForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/login')
	else:
		form = registerForm()
	return render(request, 'register.html', {'form': form})

@decorators.login_required
def logout_view(request):
	idx = 0
	for u in users:
		if u.get('username') == request.user:
			users.pop(idx)
		idx += 1
	logout(request)
	return redirect('/')

@decorators.login_required
def profile(request):
	if request.method == 'POST':
		SigForm = profileSigForm(request.POST, instance=request.user.profile)
		profileForm = profileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
		if profileForm.is_valid() and SigForm.is_valid():
			SigForm.save()
			profileForm.save()
			return redirect('/profile')
	else:
		SigForm = profileSigForm(instance=request.user.profile)
		profileForm = profileUpdateForm(instance=request.user.profile)

	return render(request, 'profile.html', {'profileForm': profileForm, 'profileSig': SigForm})