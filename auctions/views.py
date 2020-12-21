from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
import datetime

from .forms import NewListing, EmptyForm, BidForm, CommentForm
from .models import User, Listing
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
    listing = callStoredProcedure('getListingById', id)[0]
    if listing:
        try:
            lastBid = callStoredProcedure('getLastBid', id)[0] 
        except IndexError:
            lastBid = None
        bidForm = BidForm()
        commentForm = CommentForm()
        comments = callStoredProcedure('getCommentsByListingId',id)

        if lastBid:
            bidForm.fields['bidValue'].widget.attrs["min"] = lastBid['bidValue'] + 1
            bidForm.fields['bidValue'].widget.attrs["value"] = lastBid['bidValue'] + 1
        else:
            bidForm.fields['bidValue'].widget.attrs["min"] = listing['basePrice'] + 1
            bidForm.fields['bidValue'].widget.attrs["value"] = listing['basePrice'] + 1
        
        watchlist = callStoredProcedure('getWatchlist', request.user.id) if request.user.is_authenticated else []     

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
    listing = callStoredProcedure('getListingById', id)[0]

    if request.method == 'POST':
        form = EmptyForm(request.POST)
        if form.is_valid():
            if listing and listing.get('active'):
                callStoredProcedure('addWatcher', id, request.user.id)

    return HttpResponseRedirect(reverse('listing', args=[id]))


@login_required
def removeFromList(request, id):
    if request.method == 'POST':
        form = EmptyForm(request.POST)
        if form.is_valid():
            callStoredProcedure('removeWatcher', id, request.user.id)

    return HttpResponseRedirect(reverse('listing', args=[id]))


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
    listing = callStoredProcedure('getListingById', id)[0]
    if request.method == "POST" and listing and listing.get('active') and listing.get('creator_id') == request.user.id:
        form = EmptyForm(request.POST)
        if form.is_valid():
            callStoredProcedure('closeBid', id)

    return HttpResponseRedirect(reverse('listing', args=[id]))


@login_required
def comment(request, id):
    listing = callStoredProcedure('getListingById', id)[0]

    if request.method == 'POST' and listing and listing['active']:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            args = [id , comment.body ,listing['creator_id'] ]
            callStoredProcedure('addComment', *args)

    return HttpResponseRedirect(reverse('listing', args=[listing['id']]))


@login_required
def watchlist(request):
    listings = callStoredProcedure('getWatchlist', request.user.id)
    category = request.GET.get('category')

    if category:
        listings = [listing for listing in listings if listing.get('category') == category]
    return render(request, 'auctions/index.html', {
        'title': 'watchlist',
        'heading': 'My watchlist',
        'listings': listings
    })


@login_required
def myListings(request, username):
    if username == request.user.username:
        category = request.GET.get('category')

        if category:
            args = [request.user.id , category]
        else :
            args = [request.user.id , None]

        listings = callStoredProcedure('getListingByUser' , *args)
        return render(request, 'auctions/index.html', {
            'title': 'my listings',
            'heading': 'My Listings',
            'listings': listings
        })
