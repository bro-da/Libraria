from unicodedata import category
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from apps.cart.models import Cart, Cart_item
from apps.category.models import Category, Sub_category
from .models import Product,Images
from apps.cart.views import _cart_id
from django.db.models import Q,Sum,Min,Max
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

#paginator
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator

# Create your views here.
def store(request,category_slug=None,sub_category_slug=None):
    all_products = Product.objects.all().filter(is_available=True).order_by('product_name')

    min_price = all_products.aggregate(Min('price'))['price__min']
    max_price = all_products.aggregate(Max('price'))['price__max']

    minimum_filter_value = request.GET.get('min_filter')
    maximum_filter_value = request.GET.get('max_filter')

    categories = None
    sub_categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)
        if maximum_filter_value != None:
            products = Product.objects.filter(
                category=categories,
                is_available=True,
                price__gte=minimum_filter_value,
                price__lte=maximum_filter_value,
            ).order_by('product_name')
        else:
            products = Product.objects.filter(
                category=categories,
                is_available=True,
            ).order_by('product_name')

        if sub_category_slug != None:
            sub_categories = get_object_or_404(Sub_category,slug=sub_category_slug)
            if maximum_filter_value != None:
                products = Product.objects.filter(
                    sub_category=sub_categories,
                    is_available=True,
                    price__gte=minimum_filter_value,
                    price__lte=maximum_filter_value,
                ).order_by('product_name')
            else:
                products = Product.objects.filter(
                    sub_category=sub_categories,
                    is_available=True,
                ).order_by('product_name')


            
        paginator = Paginator(products,3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    else:
        if maximum_filter_value != None:
            products = Product.objects.filter(
                is_available=True,
                price__gte=minimum_filter_value,
                price__lte=maximum_filter_value,
            ).order_by('product_name')
        else:
            products = Product.objects.filter(
                is_available=True,
            ).order_by('product_name')

        paginator = Paginator(products,3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = { 
        'products': paged_products,
        'product_count':product_count,
        'all':all_products,
        'min_price':min_price,
        'max_price':max_price,
    }
    return render(request,'store/store.html',context)


def product_detail(request,category_slug,sub_category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,sub_category__slug=sub_category_slug,slug=product_slug)
        in_cart = Cart_item.objects.filter(cart__cart_id = _cart_id(request),product = single_product).exists()
        images = Images.objects.filter(product=single_product)
    except Exception as e:
        raise e

    all_products = Product.objects.all().filter(is_available=True)
    context={
        'single_product':single_product,
        'in_cart':in_cart,
        'images':images,
        'all':all_products
    }
    return render(request,'store/product_detail.html',context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains = keyword) |
                Q(product_name__icontains = keyword) |
                Q(author__icontains = keyword) |
                Q(category__category_name__icontains = keyword)
            )
            paginator = Paginator(products,6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()

            context = {
                'products': paged_products,
                'product_count':product_count,
            }
            return render(request,'store/store.html',context)
        else:
            return redirect('store')
    else:
        return redirect('store')


###mine#####
# @login_required(login_url='loginpage')
# def checkouts(request,total=0,quantity=0,cart_items=None):
#     tax=0
#     grand_total=0

#     try:
#         cart=Cart.objects.get(cart_id=_cart_id(request))
#         cart_items=Cart_item.objects.filter(cart=cart,is_active=True)
#         for cart_item in cart_items:
#             total += (cart_item.product.price * cart_item.quantity)
#             quantity += cart_item.quantity
#         tax=(2 * total)/100
#         grand_total=total+tax
#     except ObjectDoesNotExist:
#         pass
#     context={
#         'total':total,
#         'quantity':quantity,
#         'cart_items':cart_items,
#         'tax':tax,
#         'grand_total':grand_total,
#     }
#     return render(request,'store/checkout.html',context)




@login_required(login_url='loginpage')
def checkouts(request,total=0,quantity=0,cart_items=None):
    tax=0
    grand_total=0

    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=Cart_item.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax=(2 * total)/100
        grand_total=total+tax
    except ObjectDoesNotExist:
        pass
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request,'store/checkout.html',context)
    