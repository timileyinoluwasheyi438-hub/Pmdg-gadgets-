from django.contrib import admin
from .models import Category, Product, Order, OrderItem,ContactMessage,TrackingEvent 
admin.site.register(ContactMessage)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_price', 'quantity', 'get_total']
    can_delete = False

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'condition', 'price', 'stock', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'condition', 'is_featured', 'is_active']
    list_editable = ['price', 'stock', 'is_featured', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description', 'processor', 'ram']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'name', 'slug', 'description', 'price', 'original_price', 'condition', 'badge', 'stock')
        }),
        ('Images', {
            'fields': ('image', 'image_url'),
            'description': 'Upload an image OR paste an external URL'
        }),
        ('Specifications', {
            'fields': ('processor', 'ram', 'storage', 'screen', 'os', 'graphics', 'battery'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'created_at', 'updated_at')
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_full_name', 'email', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('street_address', 'apartment', 'city', 'state', 'postal_code', 'country')
        }),
        ('Order Details', {
            'fields': ('status', 'subtotal', 'shipping', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# In store/admin.py

class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 1
    fields = ['title', 'location', 'note', 'timestamp']


