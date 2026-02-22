import os
import django
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageDraw

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_project.settings')
django.setup()

from shop.models import Category, Product


def create_placeholder_image(color, name):
    """Generates a simple colored placeholder image"""
    img = Image.new('RGB', (400, 400), color=color)
    d = ImageDraw.Draw(img)
    d.text((10, 10), name, fill=(255, 255, 255))

    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=85)
    return ContentFile(img_io.getvalue(), name=f"{name.replace(' ', '_').lower()}.jpg")


def populate():
    # 1. Create Categories
    categories = {
        'Rings': '#FFD700',  # Gold color
        'Necklaces': '#C0C0C0',  # Silver color
        'Earrings': '#B87333',  # Bronze/Rose Gold color
        'Bracelets': '#E5E4E2'  # Platinum color
    }

    cat_objects = {}
    for cat_name, color in categories.items():
        c, created = Category.objects.get_or_create(name=cat_name)
        cat_objects[cat_name] = c
        print(f"Category: {cat_name} {'(Created)' if created else '(Exists)'}")

    # 2. Create Products
    products = [
        {
            'name': 'Solitaire Diamond Ring',
            'category': 'Rings',
            'price': 49999.00,
            'description': 'A classic 1-carat solitaire diamond ring set in 18k white gold.',
            'color': '#1C1C1C'
        },
        {
            'name': 'Gold Plated Ruby Necklace',
            'category': 'Necklaces',
            'price': 12500.00,
            'description': 'Elegant gold-plated necklace featuring a deep red synthetic ruby pendant.',
            'color': '#8B0000'
        },
        {
            'name': 'Pearl Drop Earrings',
            'category': 'Earrings',
            'price': 3499.00,
            'description': 'Timeless freshwater pearl drop earrings with sterling silver hooks.',
            'color': '#F0F8FF'
        },
        {
            'name': 'Rose Gold Tennis Bracelet',
            'category': 'Bracelets',
            'price': 89000.00,
            'description': 'Stunning 14k rose gold tennis bracelet studded with cubic zirconia.',
            'color': '#FF69B4'
        },
        {
            'name': 'Emerald Cut Sapphire Ring',
            'category': 'Rings',
            'price': 65000.00,
            'description': 'Vintage style emerald-cut blue sapphire ring with diamond accents.',
            'color': '#00008B'
        },
        {
            'name': 'Silver Chain with Heart Pendant',
            'category': 'Necklaces',
            'price': 2500.00,
            'description': 'Minimalist 925 sterling silver chain with a small heart pendant.',
            'color': '#708090'
        },
        {
            'name': 'Kundan Studs',
            'category': 'Earrings',
            'price': 5500.00,
            'description': 'Traditional Indian Kundan stone studs suitable for festive wear.',
            'color': '#DAA520'
        },
        {
            'name': 'Platinum Band for Men',
            'category': 'Rings',
            'price': 35000.00,
            'description': 'Sleek and modern platinum band designed for daily wear.',
            'color': '#778899'
        }
    ]

    for prod_data in products:
        category = cat_objects[prod_data['category']]

        # Check if product exists to avoid duplicates
        if not Product.objects.filter(name=prod_data['name']).exists():
            image_file = create_placeholder_image(prod_data['color'], prod_data['name'])

            Product.objects.create(
                name=prod_data['name'],
                category=category,
                price=prod_data['price'],
                description=prod_data['description'],
                image=image_file
            )
            print(f"Product Created: {prod_data['name']}")
        else:
            print(f"Product Exists: {prod_data['name']}")


if __name__ == '__main__':
    print("Starting database population...")
    populate()
    print("Done! Database populated successfully.")