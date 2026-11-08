from rentelapp.models import Tbl_User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import *
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


def about(request):
    return render(request,'about.html')
    
# def view_outfits(request):
#     """Show outfits with booking option"""
#     category_id = request.GET.get('category')
#     outfits = Outfits.objects.all()

#     if category_id:
#         outfits = outfits.filter(category_id=category_id)

#     categories = Categories.objects.all()

#     return render(request, 'view_outfits.html', {
#         'outfits': outfits,
#         'categories': categories,
#         'selected_category': category_id
#     })

import re
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Tbl_User

def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def register_user(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        # Validation
        if not name or not email or not password or not phone_number or not address:
            messages.error(request, "All fields are required!")
            return redirect('register')

        if not is_valid_email(email):
            messages.error(request, "Invalid email format!")
            return redirect('register')

        if not is_valid_phone(phone_number):
            messages.error(request, "Phone number must be 10 digits!")
            return redirect('register')

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters!")
            return redirect('register')

        # Save user
        Tbl_User.objects.create(
            name=name,
            email=email,
            password=password,
            phone_number=phone_number,
            address=address
        )

        messages.success(request, "Registration successful!")
        return redirect('login')

    return render(request, 'register.html')

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the user exists and the password matches
        user =Tbl_User.objects.filter(email=email, password=password,status='active').first()
        admin = Admin.objects.filter(email=email, password=password).first()

        if user:
            request.session['id'] = user.id
            request.session['role'] = 'user'
            return render(request, 'user_index.html', {'message': 'Login successful! Welcome back, user!', 'message_type': 'success'}) 

        elif admin:
            
            request.session['id'] = admin.id
            request.session['role'] = 'admin'
            return render(request, 'admin_index.html', {'message': 'Login successful! Welcome back, admin!', 'message_type': 'success'})
        else:
            # Failed login
            return render(request, 'login.html', {'message': 'Invalid credentials, please try again!'})
    return render(request, 'login.html')
    
def logout_view(request):
    request.session.flush()  # Clears all session data, including session ID
    return redirect("login") 
    
def index(request):
    return render(request,'index.html')

from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone

def admin_index(request):

    # ✅ Total Orders
    total_orders = Booking.objects.count()

    # ✅ Total Outfits
    total_outfits = Outfits.objects.count()

    # ✅ Active Rentals (only ongoing)
    active_rentals = Booking.objects.filter(status='ordered').count()

    # ✅ Total Users
    total_users = Tbl_User.objects.count()

    # ✅ Current Month Revenue (ONLY PAID)
    now = timezone.now()

    revenue = Payment.objects.filter(
        status='Paid',  # important!
        booking__booking_date__month=now.month,
        booking__booking_date__year=now.year
    ).aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'admin_index.html', {
        'total_orders': total_orders,
        'total_outfits': total_outfits,
        'active_rentals': active_rentals,
        'total_users': total_users,
        'revenue': revenue,
    })

import random

def user_index(request):
    user_id = request.session.get('id')

    total_orders = 0
    active_orders = 0
    wishlist_count = 0
    total_spent = 0
    recent_orders = []

    if user_id:
        total_orders = Booking.objects.filter(user_id=user_id).count()

        active_orders = Booking.objects.filter(
            user_id=user_id,
            status='ordered'
        ).count()

        wishlist_count = Wishlist.objects.filter(user_id=user_id).count()

        total_spent = Payment.objects.filter(
            booking__user_id=user_id
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        recent_orders = Booking.objects.filter(user_id=user_id)\
            .select_related('outfit')\
            .order_by('-booking_date')[:3]

    # ✅ GET RANDOM 3 OUTFITS
    all_outfits = list(Outfits.objects.all())
    featured_outfits = random.sample(all_outfits, min(len(all_outfits), 3))
    # Add this helper property dynamically
    for outfit in featured_outfits:
        outfit.is_available = any(s.quantity > 0 for s in outfit.sizes.all())

    return render(request, 'user_index.html', {
        'total_orders': total_orders,
        'active_orders': active_orders,
        'wishlist_count': wishlist_count,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'featured_outfits': featured_outfits   # ✅ NEW
    })



def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        requires_size = request.POST.get("requires_size") == 'on'
        if name:
            Categories.objects.create(name=name, requires_size=requires_size)
            return redirect("add_category")
    
    categories = Categories.objects.all()
    return render(request, "admin_add_category.html", {"categories": categories})

    from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Categories
import json

@csrf_exempt
def update_category(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        category = Categories.objects.get(id=id)
        category.name = data['name']
        category.requires_size = data['requires_size']
        category.save()
        return JsonResponse({'name': category.name, 'requires_size': category.requires_size})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Categories

@csrf_exempt
def delete_category(request, id):
    if request.method == 'POST':   # ✅ FIXED

        try:
            category = Categories.objects.get(id=id)
            category.delete()
            return JsonResponse({'status': 'success'})
        
        except Categories.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid request'}, status=400)



import decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Outfits
import decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Outfits, Categories
import decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Outfits, Categories, OutfitSize
import decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Outfits, Categories, OutfitSize


def add_outfit(request):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]

    categories = Categories.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        name = request.POST.get("name", "").strip()
        price_value = request.POST.get("price", "").strip()
        description = request.POST.get("description", "").strip()
        delivery_date=request.POST.get("delivery_date")
        image = request.FILES.get("image")

        # ✅ PRICE VALIDATION
        try:
            price = decimal.Decimal(price_value)
        except:
            return HttpResponse("Invalid price")

        # ✅ CATEGORY
        category = None
        if category_id:
            try:
                category = Categories.objects.get(id=category_id)
            except:
                return HttpResponse("Invalid category")

        # ✅ CREATE OUTFIT
        outfit = Outfits.objects.create(
            category=category,
            name=name,
            price=price,
            description=description,
            image=image,
            delivery_date=delivery_date
        )

        # ================= SIZE LOGIC =================
        if category and category.requires_size:

            has_size = False  # to ensure at least one size added

            for size_code, size_label in SIZE_CHOICES:
                qty = request.POST.get(f"qty_{size_code}")

                if qty:
                    try:
                        qty = int(qty)

                        if qty > 0:
                            OutfitSize.objects.create(
                                outfit=outfit,
                                size=size_code,
                                quantity=qty
                            )
                            has_size = True

                    except:
                        pass

            if not has_size:
                outfit.delete()
                return HttpResponse("Please enter quantity for at least one size")

        else:
            # ✅ NO SIZE → single stock
            qty = request.POST.get("quantity")

            try:
                qty = int(qty)
            except:
                qty = 1

            OutfitSize.objects.create(
                outfit=outfit,
                size="FREE",
                quantity=qty
            )

        return redirect("admin_view_outfit")

    return render(request, "add_outfits.html", {
        "categories": categories,
        "size_choices": SIZE_CHOICES
    })



from django.shortcuts import render
from .models import Outfits, Categories
from django.shortcuts import render
from .models import Outfits

def admin_view_outfit(request):
    search_query = request.GET.get('search', '')

    outfits = Outfits.objects.filter(name__icontains=search_query).prefetch_related('sizes')

    return render(request, 'admin_view_outfit.html', {
        'outfits': outfits
    })


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Outfits
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import Outfits
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import Outfits

@require_http_methods(["POST"])
def delete_outfit(request, outfit_id):
    outfit = get_object_or_404(Outfits, id=outfit_id)
    outfit.delete()   # 🔥 will also delete sizes automatically
    return JsonResponse({'message': 'Outfit deleted successfully.'}, status=200)


from django.shortcuts import render, get_object_or_404, redirect
from .models import Outfits, Categories  

from django.shortcuts import render, get_object_or_404, redirect
from .models import Outfits, Categories, OutfitSize
import decimal

def edit_outfit(request, outfit_id):
    outfit = get_object_or_404(Outfits, id=outfit_id)
    categories = Categories.objects.all()

    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]

    if request.method == 'POST':
        outfit.name = request.POST.get('name')
        outfit.category_id = request.POST.get('category')

        try:
            outfit.price = decimal.Decimal(request.POST.get('price'))
        except:
            pass

        outfit.description = request.POST.get('description')
        outfit.delivery_date = request.POST.get('delivery_date')

        if request.FILES.get('image'):
            outfit.image = request.FILES['image']

        outfit.save()

        # 🔥 DELETE OLD SIZE DATA
        OutfitSize.objects.filter(outfit=outfit).delete()

        category = outfit.category

        # ================= SIZE LOGIC =================
        if category and category.requires_size:
            for size_code, _ in SIZE_CHOICES:
                qty = request.POST.get(f"qty_{size_code}")

                if qty:
                    try:
                        qty = int(qty)
                        if qty > 0:
                            OutfitSize.objects.create(
                                outfit=outfit,
                                size=size_code,
                                quantity=qty
                            )
                    except:
                        pass
        else:
            # NO SIZE
            qty = request.POST.get("quantity", 1)

            try:
                qty = int(qty)
            except:
                qty = 1

            OutfitSize.objects.create(
                outfit=outfit,
                size="FREE",
                quantity=qty
            )

        return redirect('admin_view_outfit')

    # 🔥 SEND EXISTING SIZE DATA TO HTML
    size_data = {
        s.size: s.quantity for s in outfit.sizes.all()
    }

    return render(request, 'edit_outfit.html', {
        'outfit': outfit,
        'categories': categories,
        'size_choices': SIZE_CHOICES,
        'size_data': size_data
    })


from django.shortcuts import render, get_object_or_404
from .models import Outfits, Feedback

def outfit_details(request, outfit_id):
    outfit = get_object_or_404(
        Outfits.objects.select_related('category').prefetch_related('sizes'),
        id=outfit_id
    )

    feedbacks = Feedback.objects.filter(outfit=outfit).select_related('user').order_by('-created_at')

    total = feedbacks.count()
    avg_rating = round(sum(f.rating for f in feedbacks) / total, 1) if total else 0
    rating_counts = {i: feedbacks.filter(rating=i).count() for i in range(5, 0, -1)}

    return render(request, 'outfit_details.html', {
        'outfit': outfit,
        'feedback': feedbacks,
        'total_reviews': total,
        'avg_rating': avg_rating,
        'rating_counts': rating_counts,
    })


# user

from django.shortcuts import render, get_object_or_404
from .models import Outfits, Wishlist

from django.shortcuts import render, get_object_or_404
from .models import Outfits, Wishlist

from .models import Categories

def user_view_outfit(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category')

    outfits = Outfits.objects.filter(name__icontains=search_query)\
                             .select_related('category')\
                             .prefetch_related('sizes')

    # ✅ CATEGORY FILTER
    if category_id:
        outfits = outfits.filter(category_id=category_id)

    # availability
    for outfit in outfits:
        outfit.is_available = any(s.quantity > 0 for s in outfit.sizes.all())
        outfit.total_quantity = sum(s.quantity for s in outfit.sizes.all())

    categories = Categories.objects.all()

    user_id = request.session.get('id')
    wishlist_ids = []

    if user_id:
        wishlist_ids = Wishlist.objects.filter(user_id=user_id)\
                                       .values_list('outfit_id', flat=True)

    return render(request, 'user_view_outfit.html', {
        'outfits': outfits,
        'wishlist_ids': list(wishlist_ids),
        'categories': categories  # ✅ ADD THIS
    })

def user_view_outfit_details(request, outfit_id):
    outfit = get_object_or_404(
        Outfits.objects.select_related('category').prefetch_related('sizes'),
        id=outfit_id
    )

    outfit.is_available = any(s.quantity > 0 for s in outfit.sizes.all())

    # Fetch feedbacks for this outfit
    feedbacks = Feedback.objects.filter(outfit=outfit).select_related('user').order_by('-created_at')

    # Rating summary
    total = feedbacks.count()
    avg_rating = round(sum(f.rating for f in feedbacks) / total, 1) if total else 0
    rating_counts = {i: feedbacks.filter(rating=i).count() for i in range(5, 0, -1)}

    similar_outfits = Outfits.objects.filter(
        category=outfit.category
    ).exclude(id=outfit_id)[:3] if outfit.category else []

    return render(request, 'user_view_outfit_details.html', {
        'outfit': outfit,
        'feedbacks': feedbacks,
        'avg_rating': avg_rating,
        'total_reviews': total,
        'rating_counts': rating_counts,
        'similar_outfits': similar_outfits,
    })

# def user_view_outfit_details(request, outfit_id):
#     outfit = get_object_or_404(
#         Outfits.objects.select_related('category').prefetch_related('sizes'),
#         id=outfit_id
#     )

#     return render(request, 'user_view_outfit_details.html', {
#         'outfit': outfit
#     })



from django.shortcuts import render, redirect, get_object_or_404
from .models import Outfits, Booking, Payment, Notification, Tbl_User
from django.contrib import messages
import re
from django.views.decorators.csrf import csrf_exempt
from .models import Outfits, Booking, OutfitSize
def book_outfit(request, outfit_id):
    outfit = get_object_or_404(Outfits, id=outfit_id)
    user_id = request.session.get('id')

    if not user_id:
        return redirect('login')

    user = get_object_or_404(Tbl_User, id=user_id)

    # ✅ FIXED
    size_id = request.GET.get('selected_size_id') or request.POST.get('selected_size_id')

    if not size_id:
        messages.error(request, "Please select a size")
        return redirect('user_view_outfit_details', outfit_id=outfit.id)

    size_obj = get_object_or_404(OutfitSize, id=size_id)

    if request.method == 'POST':

        if size_obj.quantity <= 0:
            messages.error(request, "Selected size is out of stock")
            return redirect('user_view_outfit_details', outfit_id=outfit.id)

        booking = Booking.objects.create(
            outfit=outfit,
            user=user,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone_number=request.POST.get('phone_number'),
            size=size_obj.size,
            size_obj=size_obj,
            address=request.POST.get('address') or user.address
        )

        return redirect('payment', booking_id=booking.id)

    return render(request, 'book_outfit.html', {
        'outfit': outfit,
        'user': user
    })

import re
from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    amount = booking.outfit.price / 2

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        # ===== PAYMENT VALIDATION SAME AS YOUR CODE =====

        Payment.objects.create(
            booking=booking,
            amount=amount,
            card_holder_name="UPI" if payment_method == "upi" else request.POST.get('card_holder_name'),
            card_number=request.POST.get('upi_id') if payment_method == "upi" else request.POST.get('card_number'),
            cvv="000" if payment_method == "upi" else request.POST.get('cvv'),
            expiry_date="00/00" if payment_method == "upi" else request.POST.get('expiry_date'),
            upi_id=request.POST.get('upi_id') if payment_method == "upi" else None  # ✅ ADD
        )

        # ✅ STOCK REDUCTION (CORRECT)
        size_obj = booking.size_obj

        if size_obj:
            size_obj.quantity -= 1
            size_obj.save()

            # 🔥 NOTIFICATIONS
            if size_obj.quantity == 0:
                Notification.objects.create(
                    user=booking.user,
                    message=f"{booking.outfit.name} ({size_obj.size}) is OUT OF STOCK!"
                )

            elif size_obj.quantity <= 2:
                Notification.objects.create(
                    user=booking.user,
                    message=f"{booking.outfit.name} ({size_obj.size}) is LOW STOCK ({size_obj.quantity} left)"
                )

        # booking notification
        Notification.objects.create(
            user=booking.user,
            message=f"New booking placed for {booking.outfit.name}"
        )

        messages.success(request, "Payment successful ❤️")
        return redirect('success_booking', booking_id=booking.id)

    return render(request, 'payment.html', {
        'booking': booking,
        'amount': amount
    })
def success_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'success_booking.html', {'booking': booking})

def my_orders(request):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('login')

    bookings = Booking.objects.filter(
        user_id=user_id
    ).select_related('outfit').prefetch_related(
        'payment_set', 'feedback'        # prefetch both in one shot
    ).order_by('-booking_date')

    paid_count    = sum(1 for b in bookings if b.payment_set.exists())
    pending_count = sum(1 for b in bookings if not b.payment_set.exists())
    cancelled_count = sum(1 for b in bookings if b.status == "cancelled")

    return render(request, 'my_orders.html', {
        'bookings':      bookings,
        'paid_count':    paid_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
    })
from django.shortcuts import render
from .models import Notification

def admin_notifications(request):
    if request.session.get('role') != 'admin':
        return redirect('login')  # Redirect if not admin

    # Fetch all notifications ordered by latest first
    notifications = Notification.objects.all().order_by('-created_at')

    return render(request, 'admin_notifications.html', {'notifications': notifications})



def success_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payment = Payment.objects.get(booking=booking)  # Get the payment details

    return render(request, 'success_booking.html', {'booking': booking, 'payment': payment})



from django.shortcuts import render, get_object_or_404, redirect
from .models import Booking, Payment

from django.shortcuts import render, redirect
from django.db.models import Count, Q
from .models import Booking, Payment

def admin_view_orders(request):

    # ✅ Admin check
    if request.session.get('role') != 'admin':
        return redirect('login')

    # ✅ All orders
    orders = Booking.objects.all().order_by('-booking_date')

    # ✅ Counts
    total_orders = orders.count()

    # ✅ Paid Orders (Payment exists AND status Paid)
    paid_count = Booking.objects.filter(
        payment__status='Paid'
    ).distinct().count()

    # ✅ Pending Orders (ordered but no payment)
    pending_count = Booking.objects.filter(
        status='ordered',
        payment__isnull=True
    ).count()

    # ✅ Cancelled Orders
    cancelled_count = Booking.objects.filter(
        status='cancelled'
    ).count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
    }

    return render(request, 'admin_orders.html', context)



def view_payment_details(request, order_id):
    # Check if the user is an admin
    if request.session.get('role') != 'admin':
        return redirect('login')  # Redirect to login if not an admin

    order = get_object_or_404(Booking, id=order_id)
    payment = Payment.objects.filter(booking=order).first()  # Get payment for the order

    return render(request, 'payment_details.html', {'order': order, 'payment': payment})


import re
from django.contrib import messages
from django.shortcuts import redirect, render

def view_profile(request):
    user = request.session.get('id')
    if not user:
        return redirect('login')
    user_obj = Tbl_User.objects.get(id=user)
    return render(request, 'view_profile.html', {'user': user_obj})


def update_profile(request):
    user = request.session.get('id')
    if not user:
        return redirect('login')
    user_obj = Tbl_User.objects.get(id=user)

    if request.method == 'POST':
        name         = (request.POST.get('name') or '').strip()
        email        = (request.POST.get('email') or '').strip()
        phone_number = (request.POST.get('phone_number') or '').strip()
        password     = (request.POST.get('password') or '').strip()
        address      = (request.POST.get('address') or '').strip()

        # Validations
        if not re.match(r"^[A-Za-z][A-Za-z .'\-]*[A-Za-z]$", name):
            messages.error(request, "Invalid name. Letters only.")
            return redirect('update_profile')

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            messages.error(request, "Invalid email address.")
            return redirect('update_profile')

        if not re.match(r"^\+?[\d\s\-]{7,15}$", phone_number):
            messages.error(request, "Invalid phone number.")
            return redirect('update_profile')

        if not address:
            messages.error(request, "Address cannot be empty.")
            return redirect('update_profile')

        user_obj.name         = name
        user_obj.email        = email
        user_obj.phone_number = phone_number
        user_obj.address      = address

        if password:
            if len(password) < 6:
                messages.error(request, "Password must be at least 6 characters.")
                return redirect('update_profile')
            user_obj.password = password  # hash this if you add auth later

        user_obj.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('view_profile')

    return render(request, 'update_profile.html', {'user': user_obj})



from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

def add_feedback(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Only allow if paid
    if not booking.payment_set.exists():
        messages.error(request, "You can only review outfits you have paid for.")
        return redirect('my_orders')

    # Prevent duplicate feedback
    if Feedback.objects.filter(booking=booking).exists():
        messages.info(request, "You have already submitted feedback for this booking.")
        return redirect('my_orders')

    if request.method == 'POST':
        rating  = request.POST.get('rating', '').strip()
        comment = request.POST.get('comment', '').strip()

        if not rating or not rating.isdigit() or int(rating) not in range(1, 6):
            messages.error(request, "Please select a rating between 1 and 5.")
            return redirect('add_feedback', booking_id=booking.id)

        Feedback.objects.create(
            booking=booking,
            user=booking.user,
            outfit=booking.outfit,
            rating=int(rating),
            comment=comment,
        )
        messages.success(request, "Thank you for your feedback!")
        return redirect('my_orders')

    return render(request, 'add_feedback.html', {'booking': booking})


def toggle_wishlist(request, outfit_id):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('login')

    outfit = get_object_or_404(Outfits, id=outfit_id)
    user   = get_object_or_404(Tbl_User, id=user_id)

    existing = Wishlist.objects.filter(user=user, outfit=outfit).first()
    if existing:
        existing.delete()
        messages.success(request, f"'{outfit.name}' removed from your wishlist.")
    else:
        Wishlist.objects.create(user=user, outfit=outfit)
        messages.success(request, f"'{outfit.name}' added to your wishlist.")

    # Go back to wherever the user came from
    return redirect(request.META.get('HTTP_REFERER', 'view_wishlist'))


def view_wishlist(request):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('login')

    items = Wishlist.objects.filter(
        user_id=user_id
    ).select_related('outfit').order_by('-added_at')

    return render(request, 'wishlist.html', {'items': items})

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status == "cancelled":
        messages.warning(request, "Booking already cancelled!")
        return redirect('my_orders')

    # Update status
    booking.status = "cancelled"
    booking.save()

    # ✅ RESTORE STOCK (IMPORTANT FIX)
    if booking.size_obj:
        booking.size_obj.quantity += 1
        booking.size_obj.save()

    messages.success(request, "Booking cancelled. Advance amount will be refunded 💰")

    return redirect('my_orders')
def admin_view_feedback(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    feedback = Feedback.objects.all().order_by('-created_at')
    return render(request, 'admin_view_feedback.html', {'feedback': feedback})


def admin_view_users(request):
    if request.session.get('role') != 'admin':
        return redirect('login')

    users = Tbl_User.objects.all().order_by('-id')

    return render(request, 'admin_users.html', {'users': users})



def block_user(request, id):
    user = Tbl_User.objects.get(id=id)
    user.status = 'blocked'
    user.save()
    return redirect('admin_view_users')


def unblock_user(request, id):
    user = Tbl_User.objects.get(id=id)
    user.status = 'active'
    user.save()
    return redirect('admin_view_users')