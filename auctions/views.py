from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import NewListing, EmptyForm, BidForm, CommentForm
from .models import User, Listing, Watcher
from .utils import callStoredProcedure, getDateTime


def index(request):
    category = request.GET.get('category')

    listings = callStoredProcedure("getAllActiveListings")

    if category:
        listings = [listing for listing in listings if listing.get('category') == category]

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
            args = [listing.title, listing.description, listing.imageURL, listing.creator_id, listing.basePrice,
                    listing.category, getDateTime(), listing.active, ]
            listing = callStoredProcedure("createListing", *args)[0]
            return HttpResponseRedirect(reverse('listing', args=[listing['id']]))
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

        watchlist = [temp.listing for temp in request.user.watchlist.all()] if request.user.is_authenticated else []

        return render(request, 'auctions/listing.html', {
            "listing": listing,
            "bidForm": bidForm,
            'commentForm': commentForm,
            'comments': comments,
            'watchlist': watchlist
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
            if listing and listing.active:
                watcher = Watcher(user=request.user, listing=listing)
                watcher.save()

    return HttpResponseRedirect(reverse('listing', args=[listing.id]))


@login_required
def removeFromList(request, id):
    listing = Listing.objects.get(id=id)

    if request.method == 'POST':
        form = EmptyForm(request.POST)
        if form.is_valid() and listing:
            watcher = request.user.watchlist.filter(listing=listing.id)
            if watcher:
                watcher.delete()

    return HttpResponseRedirect(reverse('listing', args=[listing.id]))


@login_required
def placeBid(request, id):
    listing = callStoredProcedure('getListingById', id)[0]
    message = "Bid placed succesfully!"

    if request.method == 'POST':
        if listing and listing.get('active'):
            form = BidForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                lastBid = callStoredProcedure('getLastBid', id)[0]

                if lastBid:
                    if form.bidValue > lastBid.get('bidValue'):
                        callStoredProcedure('placeBid', id, form.bidValue, request.user.id, getDateTime())
                    else:
                        message = "Bid not placed. Bid value must be greater than the last bid value - " + str(
                            lastBid.get('bidValue')) + "."
                else:
                    if form.bidValue > listing.get('basePrice'):
                        callStoredProcedure('placeBid', id, form.bidValue, request.user.id, getDateTime())
                    else:
                        message = "Bid not placed. Bid value must be greater than the base price - " + str(
                            listing.get('basePrice')) + "."
    print(message)
    return HttpResponseRedirect(reverse('listing', args=[listing.get('id')]))


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
    watchlist = request.user.watchlist.all()
    listings = [temp.listing for temp in watchlist]
    category = request.GET.get('category')

    if category:
        listings = [listing for listing in listings if listing.category == category]

    return render(request, 'auctions/index.html', {
        'title': 'watchlist',
        'heading': 'My watchlist',
        'listings': listings
    })


@login_required
def myListings(request, username):
    if username == request.user.username:
        user = User.objects.get(username=username)
        listings = Listing.objects.filter(creator=user).order_by("timestamp").reverse()

        category = request.GET.get('category')

        if category:
            listings = listings.filter(category=category)

        return render(request, 'auctions/index.html', {
            'title': 'my listings',
            'heading': 'My Listings',
            'listings': listings.all()
        })
