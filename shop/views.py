import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Cart, CartItem, Order

# Initialize Razorpay Client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/index.html', {'products': products})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Get the user's cart
    cart = get_object_or_404(Cart, user=request.user)
    # Get the specific item in that cart
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        # If quantity is 1, removing it should delete the record
        cart_item.delete()
        redirect('view_cart')

    return redirect('view_cart')

@login_required
def delete_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)

    # Filter and delete the item record immediately
    CartItem.objects.filter(cart=cart, product=product).delete()

    return redirect('view_cart')


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    total = sum(item.total_price() for item in items)
    return render(request, 'shop/cart.html', {'items': items, 'total': total})


@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.cartitem_set.all()
    total_amount = sum(item.total_price() for item in items)

    # Razorpay expects amount in paise (multiply by 100)
    amount_in_paise = int(total_amount * 100)

    # Create Order on Razorpay
    # data = {"amount": amount_in_paise, "currency": "INR", "payment_capture":"1", "receipt": "order_rcptid_11"}
    data = {"amount": amount_in_paise, "currency": "INR", "payment_capture":"1"}
    payment_order = client.order.create(data=data)

    # Create local order
    order = Order.objects.create(
        user=request.user,
        razorpay_order_id=payment_order['id'],
        total_amount=total_amount
    )

    context = {
        'order': order,
        'razorpay_order_id': payment_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount_in_paise,
        'currency': 'INR'
    }
    return render(request, 'shop/checkout.html', context)


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Verify Signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            # Update Order Status
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.razorpay_payment_id = razorpay_payment_id
            order.payment_status = 'Paid'
            order.save()

            # Clear Cart
            Cart.objects.get(user=order.user).delete()

            return render(request, 'shop/success.html')
        except:
            return render(request, 'shop/failure.html')