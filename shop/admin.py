from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order


# --- Inlines ---

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1  # Number of empty slots to show for new items
    fields = ('product', 'quantity', 'get_unit_price')
    readonly_fields = ('get_unit_price',)

    def get_unit_price(self, obj):
        return f"₹{obj.product.price}"

    get_unit_price.short_description = 'Unit Price'


# --- Model Admin Classes ---

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    list_editable = ('price',)  # Allows quick price updates from the list view


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email')
    inlines = [CartItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('razorpay_order_id', 'razorpay_payment_id', 'user__username')
    readonly_fields = ('created_at',)

    # Color-code the payment status for better visibility
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form
