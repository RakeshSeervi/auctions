from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Listing
from .forms import NewListing, EmptyForm, BidForm, CommentForm


def index(request):
    listings = Listing.objects.filter(active=True)
    category = request.GET.get('category')
    if category:
        listings = listings.filter(category=category)

    return render(request, "auctions/index.html", {
        'title': 'home',
        'heading': 'Active listings',
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        next = "index"
        if request.POST["next"]:
            next = request.POST["next"]

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect(next)
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    listing = NewListing()
    if request.method == 'POST':
        listing = NewListing(request.POST)
        if listing.is_valid():
            listing = listing.save(commit=False)
            listing.creator = request.user
            listing.save()
            return HttpResponseRedirect(reverse('listing', args=[listing.id]))
    return render(request, 'auctions/new.html', {
        "form": listing
    })


def listing(request, id):
    listing = Listing.objects.filter(id=id).first()
    if listing:
        lastBid = listing.bids.last()
        bidForm = BidForm()
        commentForm = CommentForm()

        comments = listing.comments.all()

        if lastBid:
            bidForm.fields['bidValue'].widget.attrs["min"] = lastBid.bidValue + 1
            bidForm.fields['bidValue'].widget.attrs["value"] = lastBid.bidValue + 1
        else:
            bidForm.fields['bidValue'].widget.attrs["min"] = listing.basePrice + 1
            bidForm.fields['bidValue'].widget.attrs["value"] = listing.basePrice + 1

        return render(request, 'auctions/listing.html', {
            "listing": listing,
            "bidForm": bidForm,
            'commentForm': commentForm,
            'comments': comments
        })
    else:
        return render(request, "auctions/error.html", {
            "message": "Error 404: Requested listing not found."
        })


@login_required
def addToList(request, id):
    listing = Listing.objects.get(id=id)

    if request.method == 'POST':
        form = EmptyForm(request.POST)
        if form.is_valid():
            if listing and listing.active and listing not in request.user.watchlist.all():
                request.user.watchlist.add(listing)
                request.user.save()

    return HttpResponseRedirect(reverse('listing', args=[listing.id]))


@login_required
def removeFromList(request, id):
    listing = Listing.objects.get(id=id)

    if request.method == 'POST':
        form = EmptyForm(request.POST)
        if form.is_valid():
            if listing and listing in request.user.watchlist.all():
                request.user.watchlist.remove(listing)
                request.user.save()

    return HttpResponseRedirect(reverse('listing', args=[listing.id]))


@login_required
def placeBid(request, id):
    listing = Listing.objects.get(id=id)

    if request.method == 'POST':
        if listing and listing.active:
            form = BidForm(request.POST)
            if form.is_valid():
                # check for value
                form = form.save(commit=False)
                form.bidObject = listing
                form.bidder = request.user
                form.save()

    return HttpResponseRedirect(reverse('listing', args=[listing.id]))


@login_required
def close(request, id):
    listing = Listing.objects.get(id=id)
    if request.method == "POST" and listing and listing.active and listing.creator == request.user:
        form = EmptyForm(request.POST)
        if form.is_valid():
            listing.active = False

            if listing.bids.count() > 0:
                listing.winner = listing.bids.last().bidder
            listing.save()

    return HttpResponseRedirect(reverse('listing', args=[listing.id]))


@login_required
def comment(request, id):
    listing = Listing.objects.get(id=id)

    if request.method == 'POST' and listing and listing.active:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.object = listing
            comment.save()

    return HttpResponseRedirect(reverse('listing', args=[listing.id]))


@login_required
def watchlist(request):
    listings = request.user.watchlist
    category = request.GET.get('category')

    if category:
        listings = listings.filter(category=category)

    return render(request, 'auctions/index.html', {
        'title': 'watchlist',
        'heading': 'My watchlist',
        'listings': listings.all()
    })


def myListings(request, username):
    if username == request.user.username:
        user = User.objects.get(username=username)
        listings = Listing.objects.filter(creator=user)

        category = request.GET.get('category')

        if category:
            listings = listings.filter(category=category)

        return render(request, 'auctions/index.html', {
            'title': 'my listings',
            'heading': 'My Listings',
            'listings': listings.all()
        })
