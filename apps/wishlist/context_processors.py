from apps.category.models import category
from apps.wishlist.models import wishlist
from django.shortcuts import render,redirect,get_object_or_404
from apps.wishlist.views import _wishlist_id, wishlist
from django.core.exceptions import ObjectDoesNotExist



def wishlists(request,wishlist=0):
    wish_counter=0
    wishlist_itams=None
    if 'admin' in request.path:
        return{}
    else:
        try:
            wishlist = wishlist.objects.get(wishlist_id=_wishlist_id(request))
            wishlist_itams=wishlistItem.objects.filter(wishlist=wishlist, is_active = True),
            if wishlist_itams!=0:
                wish_counter=WishlistItem.objects.filter(wishlist=wishlist, is_active = True).count()
            else:
                wish_counter=0
        except wishlist.DoesNotExist:
            wish_counter=0
            pass
    return {
       'wishlist_itams':WishlistItem.objects.filter(wishlist=wishlist, is_active = True),
       'wish_counter':wish_counter,
     }