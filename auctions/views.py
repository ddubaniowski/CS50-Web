from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from datetime import datetime

from .models import User, Listing, Bid, Comment
from .forms import CATEGORY_CHOICES
from auctions.forms import NewListingForm, BidForm, CommentForm


def index(request):
    return render(request, "auctions/index.html", {
        "items": Listing.objects.all()
    })

@login_required
def new(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            start_bid = form.cleaned_data['start_bid']
            image_url = form.cleaned_data['image_url']
            timestamp = datetime.now()
            user = request.user.username

            # if no image provided, insert placeholder
            if image_url == "":
                image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/480px-No_image_available.svg.png"
            category = form.cleaned_data['category']

            # create listing object with form data
            item = Listing.objects.create(
                title=title,
                description=description,
                current_bid=start_bid,
                image=image_url,
                category=category,
                timestamp=timestamp,
                user=user)
            item.save()

            return HttpResponseRedirect(reverse("index"))
    else:
        form = NewListingForm()

    return render(request, "auctions/new.html", {
        "form": form
    })

def listing(request, item_id):
    login = request.user.is_authenticated
    item = Listing.objects.get(pk=item_id)
    comments = Comment.objects.filter(item=item)

    # display full details if user logged in
    if login:
        user = get_object_or_404(User, pk=request.user.id)
        watchlist = user.watchlist.all()

        # redirect to closed listing page if true
        if item.closed:
            return HttpResponseRedirect(reverse("closed", args=(item_id,)))

        # check if user who posted listing is logged in
        if user.username == item.user:
            check = True
        else:
            check = False

        if request.method == "POST":
            try:
                # first check if bid form was submitted, otherwise go to KeyError except
                check = request.POST['bid']
                form = BidForm(request.POST)
                if form.is_valid():
                    # create new bid object and save new item price
                    new_bid = form.cleaned_data['bid']
                    if new_bid < item.current_bid:
                        # return error if bid smaller
                        return render(request, "auctions/error.html")
                    item.current_bid = new_bid
                    item.winner_id = request.user.id
                    item.save()
                    bid = Bid(bid=new_bid, user=user, item=item)
                    bid.save()
                    bids = Bid.objects.filter(item=item)
                    count = len(bids)

                    form = BidForm()
                    # check if item in watchlist
                    if item in watchlist:
                        watch = True
                    else:
                        watch = False

                    return render(request, "auctions/listing.html", {
                        "item_id": item_id,
                        "item": item,
                        "watch": watch,
                        "form": form,
                        "count": count,
                        "login": login,
                        "check": check
                    })

            except KeyError:
                # add or remove item from watchlist as required
                form = BidForm()
                if item in watchlist:
                    # remove item from watchlist
                    user.watchlist.remove(item)
                    watch = False
                else:
                    # add item to watchlist
                    user.watchlist.add(item)
                    watch = True

                bids = Bid.objects.filter(item=item)
                count = len(bids)
                return render(request, "auctions/listing.html", {
                    "item_id": item_id,
                    "item": item,
                    "watch": watch,
                    "form": form,
                    "count": count,
                    "login": login,
                    "check": check
                })

        else:
            # render template if GET method used
            form = BidForm()
            if item in watchlist:
                watch = True
            else:
                watch = False

            bids = Bid.objects.filter(item=item)
            count = len(bids)
            return render(request, "auctions/listing.html", {
                "item_id": item_id,
                "item": item,
                "watch": watch,
                "form": form,
                "count": count,
                "login": login,
                "check": check,
                "comments": comments
            })
    # display limited details if user not logged in
    else:
        return render(request, "auctions/listing.html", {
                "item_id": item_id,
                "item": item,
                "login": login
            })

def closed(request, item_id):
    # redirect to closed template if listing inactive
    item = Listing.objects.get(pk=item_id)
    item.closed = True
    # change title of listing if not already done
    if "[CLOSED]" not in item.title:
        item.title = item.title + " [CLOSED]"
    item.save()
    winner = get_object_or_404(User, pk=item.winner_id)
    # if winner logged in display message flag
    if winner == request.user:
        login = True
    else:
        login = False
    return render(request, "auctions/closed.html", {
        "item": item,
        "winner": winner,
        "login": login
    })

@login_required
def comment(request, item_id):
    # view for submitting a new comment form
    item = Listing.objects.get(pk=item_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            # create and save new comment object with form data
            text = form.cleaned_data['comment']
            user = get_object_or_404(User, pk=request.user.id)
            timestamp = datetime.now()
            comment = Comment.objects.create(
                user=user,
                comment=text,
                timestamp=timestamp,
                item=item)
            comment.save()
            return HttpResponseRedirect(reverse("listing", args=(item_id,)))
    else:
        # otherwise GET comment page
        form = CommentForm()
        return render(request, "auctions/comment.html", {
            "form": form,
            "item_id": item_id
        })

@login_required
def categories(request):
    # create list of categories to pass to template
    choices = []
    for choice in CATEGORY_CHOICES:
        choices.append(choice[0])
    return render(request, "auctions/categories.html", {
        "categories": choices
    })

@login_required
def category(request, category):
    items = Listing.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        "items": items
    })


@login_required
def watchlist(request):
    user = get_object_or_404(User, pk=request.user.id)
    watchlist = user.watchlist.all()
    count = len(watchlist)
    return render(request, "auctions/watch.html", {
        "watchlist": watchlist,
        "count": count
    })


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
