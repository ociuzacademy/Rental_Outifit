from django.db import models

class Tbl_User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    address=models.TextField()
    status=models.CharField(max_length=20, default='active')

    def __str__(self):
        return self.name

class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=8)

class Categories(models.Model):
    SIZE_REQUIREMENT_CHOICES = [
        (True, "Requires Size"),
        (False, "No Size Required")
    ]
    name = models.CharField(max_length=100)
    requires_size = models.BooleanField(choices=SIZE_REQUIREMENT_CHOICES, default=False)

    def __str__(self):
        return self.name

class Outfits(models.Model):
    category = models.ForeignKey('Categories', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='outfits/', blank=True, null=True)
    delivery_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
            
class OutfitSize(models.Model):
    outfit = models.ForeignKey(Outfits, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.outfit.name} - {self.size} ({self.quantity})"

class Booking(models.Model):
    outfit = models.ForeignKey(Outfits, on_delete=models.CASCADE)
    user = models.ForeignKey(Tbl_User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=100)

    size = models.CharField(max_length=50, null=True, blank=True)
    size_obj = models.ForeignKey(OutfitSize, on_delete=models.SET_NULL, null=True)  # ✅ NEW

    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='ordered')
    address = models.TextField(blank=True)

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Paid')  # Payment status
    card_holder_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=16)  # Store as string for formatting
    cvv = models.CharField(max_length=3)
    expiry_date = models.CharField(max_length=5)  # MM/YY format
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Payment for {self.booking.outfit.name} by {self.booking.name}"

class Notification(models.Model):
    user = models.ForeignKey(Tbl_User, on_delete=models.CASCADE)  # Link to User
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

class Feedback(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    user    = models.ForeignKey(Tbl_User, on_delete=models.CASCADE)
    outfit  = models.ForeignKey(Outfits, on_delete=models.CASCADE)
    rating  = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.outfit.name} by {self.user.name} — {self.rating}★"

class Wishlist(models.Model):
    user   = models.ForeignKey(Tbl_User, on_delete=models.CASCADE)
    outfit = models.ForeignKey(Outfits, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'outfit')  # no duplicates

    def __str__(self):
        return f"{self.user.name} → {self.outfit.name}"