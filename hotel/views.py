from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import Hotel, Room_type, Room, Profile, Reservation, Reserved_room 
from hotel.forms import Booking
from django.contrib.auth import login, authenticate
from hotel.forms import SignUpForm
# Create your views here.

def index(request):
	hotels = Hotel.objects.all()
	return render(request, 'hotel/index.html', {'hotels' : hotels})


def contact(request):
	hotels = Hotel.objects.all()
	return render(request, 'hotel/contact.html', {'hotels' : hotels})


def offer(request):
	hotels = Hotel.objects.all()
	rooms = Room_type.objects.all()
	return render(request, 'hotel/offer.html', {'hotels' : hotels, 'rooms' : rooms})


def gallery(request):
	hotels = Hotel.objects.all()
	i, p = "123456", "123"
	return render(request, 'hotel/gallery.html', {'hotels' : hotels, 'i' : i, 'p' : p})


def sign_up(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			user.refresh_from_db()  # load the profile instance created by the signal
			user.profile.name = form.cleaned_data.get('name')
			user.profile.surname = form.cleaned_data.get('surname')
			user.profile.phone = form.cleaned_data.get('phone')
			user.profile.email = form.cleaned_data.get('email')
			user.save()
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=user.username, password=raw_password)
			login(request, user)
			return redirect('index')
	else:
		form = SignUpForm()
	return render(request, 'registration/signUp.html', {'form' : form})


def book_room(request):
	form = Booking(request.POST or None, user=request.user)
	if request.method == 'POST':
		if form.is_valid():
			if request.user.is_authenticated:
				reservation = form.save(commit=False)
				guest = Profile.objects.get(user=request.user)
				reservation.name = guest.name
				reservation.surname = guest.surname
				reservation.phone = guest.phone
				reservation.email = guest.user.email
				reservation.save()

			else:
				reservation = form.save()

			n = reservation.pk
			return redirect('bookSuccess', n)
	return render(request, 'hotel/bookRoom.html', {'form' : form})


def book_success(request, pk):
	receipts = Reservation.objects.get(reservationID=pk)
	receipts.price()
	return render(request, 'hotel/bookSuccess.html', {'receipts' : receipts})


def my_bookings(request):
	guest = Profile.objects.get(user=request.user)
	bookings = Reservation.objects.filter(
		name=guest.name
		).filter(
		surname=guest.surname
		).filter(
		phone=guest.phone
		).exclude(
		bookOut__lt=timezone.now()
		)
	return render(request, 'hotel/myBookings.html', {'bookings' : bookings})
