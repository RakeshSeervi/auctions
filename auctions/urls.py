from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.create, name="new"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("addToList/<int:id>", views.addToList, name="addToList"),
    path("removeFromList/<int:id>", views.removeFromList, name="removeFromList"),
    path("placeBid/<int:id>", views.placeBid, name="placeBid"),
    path("close/<int:id>", views.close, name="close"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<str:username>/listings", views.myListings, name="myListings")
]
