from django.shortcuts import render

users = []

def index(request):

	def searchUser(user, users):
		for u in users:
			if u.get('username') == user:
				return True
	
	def hasUpdated(user, users, fields):
		retVal = 0
		for u in users:
			if u.get('username') == user:
				if (
					u.get('profilePicture') != fields.get('profilePicture') or 
					u.get('userSignature') != fields.get('userSignature')):
					return retVal
			retVal += 1
		return -1

	if request.user.is_authenticated:
		userDetails = {
		'username': request.user,
		'profilePicture': request.user.profile.image.url,
		'userSignature': request.user.profile.signature
		}
		idx = hasUpdated(request.user, users, userDetails)
		if idx != -1 or not searchUser(request.user, users):
			if idx != -1 :
				users.pop(idx)
			users.append(userDetails)

	context = {'users': users}
	return render(request, 'index.html', context)