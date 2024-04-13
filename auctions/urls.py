from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_auction, name="create_auction"),
    path("auction/<int:auction_id>", views.auction, name="auction"),
    path("auction/<int:auction_id>/add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("auction/<int:auction_id>/remove_from_watchlist", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("auction/<int:auction_id>/place_bid", views.place_bid, name="place_bid"),
    path("auction/<int:auction_id>/close", views.close_auction, name="close_auction"),
    path("auction/<int:auction_id>/add_comment", views.add_comment, name="add_comment"),
    path("watchlist", views.watchlist, name="watchlist"),
]