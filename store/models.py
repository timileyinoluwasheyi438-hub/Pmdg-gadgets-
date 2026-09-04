from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User


class Category(models.Model):
    """Product categories: Gaming, Business, Student, Accessories."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="External image URL (Unsplash etc)")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop_category', kwargs={'category': self.slug})
    def get_image(self):
        if getattr(self, 'image', None):
           url = self.image.url
           if url.startswith('http') or url.startswith('/media/'):
              return url
           return '/media/' + url.lstrip('/')

        url = (getattr(self, 'image_url', None) or '').strip()
        if url.startswith('http') or url.startswith('/media/'):
           return url
        if url:
           return '/media/' + url.lstrip('/')

        return 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800'
    


class Product(models.Model):
    """Laptop products — new, refurbished, and used."""
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('refurbished', 'Refurbished'),
        ('used', 'Used'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.PositiveIntegerField(help_text="Price in Naira (₦)")
    original_price = models.PositiveIntegerField(blank=True, null=True, help_text="Strike-through price for deals")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="External image URL (Unsplash etc)")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    badge = models.CharField(max_length=50, blank=True, help_text="e.g. Best Seller, New, Refurbished, Gaming")
    stock = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Specifications
    processor = models.CharField(max_length=100, blank=True)
    ram = models.CharField(max_length=50, blank=True)
    storage = models.CharField(max_length=50, blank=True)
    screen = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    graphics = models.CharField(max_length=100, blank=True)
    battery = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def get_image(self):
        if self.image:
            url = self.image.url
            if url.startswith('http') or url.startswith('/media/'):
               return url
            return '/media/' + url.lstrip('/')

        url = (self.image_url or '').strip()
        if url.startswith('http') or url.startswith('/media/'):
          return url
        if url:
          return '/media/' + url.lstrip('/')

        return 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800'

    def get_discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0


class Order(models.Model):
    """Customer orders — Paystack integration ready."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,blank=True, related_name="orders")
    # Contact info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    # Shipping address
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Nigeria')

    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subtotal = models.PositiveIntegerField(default=0)
    shipping = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    paystack_ref = models.CharField(max_length=100, blank=True)
    paystack_transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} — {self.email}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class OrderItem(models.Model):
    """Individual items within an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def get_total(self):
          price = self.product_price or 0
          qty = self.quantity or 0
          return price * qty
        

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('product', 'Product question'),
        ('order', 'Order support'),
        ('warranty', 'Warranty / returns'),
        ('partnership', 'Partnership'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.get_subject_display()}"




class TrackingEvent(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='tracking_events')
    title = models.CharField(
        max_length=100,
        help_text="e.g. 'Order placed', 'Left warehouse', 'Arrived at airport', 'Out for delivery', 'Delivered'"
    )
    location = models.CharField(max_length=150, blank=True, help_text="e.g. 'Lagos, Nigeria' (optional)")
    note = models.CharField(max_length=255, blank=True, help_text="Optional extra detail shown to the customer")
    timestamp = models.DateTimeField(help_text="When this actually happened")

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Order #{self.order_id} — {self.title}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def _str_(self):
        return f"{self.user} — {self.product.name}"