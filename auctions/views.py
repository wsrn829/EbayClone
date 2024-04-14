from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Bid, Comment, Watchlist, Category


def index(request):
    auctions = Auction.objects.filter(active=True)
    return render(request, "auctions/index.html", {"auctions": auctions})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
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
def create_auction(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = Decimal(request.POST["starting_bid"])
        image_url = request.POST["image_url"]
        created_by = request.user
        category_name = request.POST["category_name"]

        category = Category.objects.get(name=category_name)

        auction = Auction(title=title, description=description, starting_bid=starting_bid, current_bid=starting_bid, image_url=image_url, category=category, created_by=created_by)
        auction.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create_auction.html")


@login_required
def auction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    bids = Bid.objects.filter(auction=auction)
    comments = Comment.objects.filter(auction=auction)
    return render(request, "auctions/auction.html", {
        "auction": auction,
        "bids": bids,
        "comments": comments
    })


@login_required
def watchlist(request):
    user = request.user
    watchlist_items = Watchlist.objects.filter(user=user)
    watchlist = [item.auction for item in watchlist_items]
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })

@login_required
def add_to_watchlist(request, auction_id):
    user = request.user
    auction = Auction.objects.get(pk=auction_id)
    watchlist = Watchlist(user=user, auction=auction)
    watchlist.save()
    return HttpResponseRedirect(reverse("watchlist"))


@login_required
def remove_from_watchlist(request, auction_id):
    user = request.user
    auction = Auction.objects.get(pk=auction_id)
    watchlist = Watchlist.objects.get(user=user, auction=auction)
    watchlist.delete()
    return HttpResponseRedirect(reverse("watchlist"))


@login_required
def place_bid(request, auction_id):
    if request.method == "POST":
        user = request.user
        auction = Auction.objects.get(pk=auction_id)
        amount = Decimal(request.POST["amount"])
        if amount <= auction.current_bid:
            return render(request, "auctions/auction.html", {
                "auction": auction,
                "message": "Bid must be greater than current bid."
            })
        bid = Bid(amount=amount, bidder=user, auction=auction)
        bid.save()
        auction.current_bid = amount
        auction.save()
        return HttpResponseRedirect(reverse("auction", args=(auction_id,)))
    else:
        return HttpResponse("Method not allowed.")

@login_required
def close_auction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    auction.active = False
    auction.save()
    return HttpResponseRedirect(reverse("index"))


@login_required
def add_comment(request, auction_id):
    user = request.user
    auction = Auction.objects.get(pk=auction_id)
    content = request.POST["content"]
    comment = Comment(content=content, commenter=user, auction=auction)
    comment.save()
    return HttpResponseRedirect(reverse("auction", args=(auction_id,)))


@login_required
def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

@login_required
def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    auctions = Auction.objects.filter(category=category, active=True)
    return render(request, "auctions/category.html", {
        "category": category,
        "auctions": auctions
    })