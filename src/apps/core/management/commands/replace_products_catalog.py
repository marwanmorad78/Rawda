from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Category, Product


CATEGORY_SPECS = [
    {
        "slug": "vegetables",
        "name": "Vegetables",
        "description": "Fresh vegetables for daily cooking.",
        "display_order": 1,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Local%20tomatoes.jpg",
    },
    {
        "slug": "fruits",
        "name": "Fruits",
        "description": "Seasonal and imported fruits.",
        "display_order": 2,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Bananas%20white%20background.jpg",
    },
    {
        "slug": "juices",
        "name": "Juices",
        "description": "Refreshing bottled and chilled juices.",
        "display_order": 3,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Orange%20juice%200001.jpg",
    },
    {
        "slug": "canned-food",
        "name": "Canned Food",
        "description": "Pantry staples and preserved foods.",
        "display_order": 4,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Canned%20food.jpg",
    },
    {
        "slug": "legumes",
        "name": "Legumes",
        "description": "Beans, lentils, chickpeas, and more.",
        "display_order": 5,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Dried%20Green%20Peas.jpg",
    },
    {
        "slug": "frozen-products",
        "name": "Frozen Products",
        "description": "Frozen vegetables and ready-to-cook essentials.",
        "display_order": 6,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Peas%20and%20carrots%20%2819675818713%29.jpg",
    },
]


PRODUCT_SPECS = [
    {
        "category_slug": "vegetables",
        "name": "Cherry Tomatoes",
        "slug": "cherry-tomatoes",
        "short_description": "Sweet cherry tomatoes for salads and sandwiches.",
        "description": "Bright, snack-friendly tomatoes for salads, breakfast plates, and quick kitchen prep.",
        "price": "0.60",
        "unit_label": "per pack",
        "sku": "VEG-CHR-001",
        "sold_by_weight": True,
        "is_featured": True,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Local%20tomatoes.jpg",
    },
    {
        "category_slug": "vegetables",
        "name": "Cucumbers",
        "slug": "cucumbers",
        "short_description": "Crunchy cucumbers for fresh daily meals.",
        "description": "Cool and crisp cucumbers for salads, pickles, and everyday family meals.",
        "price": "0.75",
        "unit_label": "per kg",
        "sku": "VEG-CUC-001",
        "sold_by_weight": True,
        "is_featured": False,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Cucumis%20sativus%20-%20K%C3%B6hler%E2%80%93s%20Medizinal-Pflanzen-193.jpg",
    },
    {
        "category_slug": "fruits",
        "name": "Gala Apples",
        "slug": "gala-apples",
        "short_description": "Crisp apples with a balanced sweet taste.",
        "description": "A family-friendly apple choice for lunch boxes, desserts, and healthy snacks.",
        "price": "1.10",
        "unit_label": "per kg",
        "sku": "FRU-GAL-001",
        "sold_by_weight": True,
        "is_featured": True,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Red_Apple.jpg",
    },
    {
        "category_slug": "fruits",
        "name": "Valencia Oranges",
        "slug": "valencia-oranges",
        "short_description": "Juicy oranges for eating or juicing.",
        "description": "Fresh oranges with a bright citrus flavor, ideal for breakfast juice and fruit bowls.",
        "price": "1.20",
        "unit_label": "per kg",
        "sku": "FRU-VAL-001",
        "sold_by_weight": True,
        "is_featured": False,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Orange-Fruit-Pieces.jpg",
    },
    {
        "category_slug": "juices",
        "name": "Apple Juice",
        "slug": "apple-juice",
        "short_description": "Smooth apple juice for a quick refreshment.",
        "description": "A chilled apple juice bottle for school lunches, family meals, and guests.",
        "price": "0.80",
        "unit_label": "per bottle",
        "sku": "JUI-APP-001",
        "is_featured": True,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Apple%20juice%20with%20apple.jpg",
    },
    {
        "category_slug": "juices",
        "name": "Mango Juice",
        "slug": "mango-juice",
        "short_description": "Sweet mango juice with a rich tropical taste.",
        "description": "A smooth mango drink that pairs nicely with snacks and chilled summer servings.",
        "price": "0.95",
        "unit_label": "per bottle",
        "sku": "JUI-MAN-001",
        "is_featured": True,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Mango%20juice.jpg",
    },
    {
        "category_slug": "canned-food",
        "name": "Tomato Paste",
        "slug": "tomato-paste",
        "short_description": "Kitchen staple for sauces and stews.",
        "description": "Practical canned tomato paste for quick sauces, rice dishes, and daily cooking.",
        "price": "0.60",
        "unit_label": "per can",
        "sku": "CAN-TOM-001",
        "is_featured": False,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Tomato%20paste.jpg",
    },
    {
        "category_slug": "canned-food",
        "name": "Canned Mushrooms",
        "slug": "canned-mushrooms",
        "short_description": "Ready-to-use mushrooms for pizza and pasta.",
        "description": "Convenient canned mushrooms for creamy sauces, pizza toppings, and quick oven dishes.",
        "price": "1.00",
        "unit_label": "per can",
        "sku": "CAN-MUS-001",
        "is_featured": True,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Canned_mushrooms.jpg",
    },
    {
        "category_slug": "legumes",
        "name": "Red Lentils",
        "slug": "red-lentils",
        "short_description": "Fast-cooking lentils for soups and healthy meals.",
        "description": "Reliable red lentils for soups, side dishes, and nutritious home-cooked meals.",
        "price": "1.40",
        "unit_label": "per kg",
        "sku": "LEG-RED-001",
        "sold_by_weight": True,
        "is_featured": True,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Red_lentils.jpg",
    },
    {
        "category_slug": "legumes",
        "name": "Chickpeas",
        "slug": "chickpeas",
        "short_description": "Pantry essential for hummus and stews.",
        "description": "Quality chickpeas for hummus, salads, soups, and slow-cooked family dishes.",
        "price": "1.55",
        "unit_label": "per kg",
        "sku": "LEG-CHK-001",
        "sold_by_weight": True,
        "is_featured": False,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/2013-11-24%2015-38-21-raw-chickpea.jpg",
    },
    {
        "category_slug": "frozen-products",
        "name": "Frozen Sweet Corn",
        "slug": "frozen-sweet-corn",
        "short_description": "Quick frozen corn for soups and side dishes.",
        "description": "A versatile frozen corn pack for salads, rice dishes, pasta, and creamy soups.",
        "price": "1.65",
        "unit_label": "per bag",
        "sku": "FRO-COR-001",
        "is_featured": True,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Frozen%20corn.jpg",
    },
    {
        "category_slug": "frozen-products",
        "name": "Frozen Okra",
        "slug": "frozen-okra",
        "short_description": "Cleaned okra ready for quick cooking.",
        "description": "A freezer-friendly okra pack that helps prepare stews and home-style dishes faster.",
        "price": "1.95",
        "unit_label": "per bag",
        "sku": "FRO-OKR-001",
        "is_featured": True,
        "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Okra.jpg",
    },
]


class Command(BaseCommand):
    help = "Replace the storefront catalog with a fresh dollar-linked product set."

    @transaction.atomic
    def handle(self, *args, **options):
        categories_by_slug = {}
        for spec in CATEGORY_SPECS:
            category, created = Category.objects.get_or_create(
                slug=spec["slug"],
                defaults={
                    "name": spec["name"],
                    "description": spec["description"],
                    "display_order": spec["display_order"],
                    "is_active": True,
                    "external_image_url": spec["external_image_url"],
                },
            )
            if not created:
                category.name = spec["name"]
                category.description = spec["description"]
                category.display_order = spec["display_order"]
                category.is_active = True
                category.external_image_url = spec["external_image_url"]
                category.save(
                    update_fields=[
                        "name",
                        "description",
                        "display_order",
                        "is_active",
                        "external_image_url",
                        "updated_at",
                    ]
                )
            categories_by_slug[spec["slug"]] = category

        deleted_count, _ = Product.objects.all().delete()

        created_products = []
        for spec in PRODUCT_SPECS:
            created_products.append(
                Product.objects.create(
                    category=categories_by_slug[spec["category_slug"]],
                    name=spec["name"],
                    slug=spec["slug"],
                    short_description=spec["short_description"],
                    description=spec["description"],
                    price=spec["price"],
                    is_price_linked_to_dollar=True,
                    unit_label=spec["unit_label"],
                    sold_by_weight=spec.get("sold_by_weight", False),
                    is_available=True,
                    is_featured=spec["is_featured"],
                    sku=spec["sku"],
                    external_image_url=spec["external_image_url"],
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Replaced {deleted_count} product rows with {len(created_products)} fresh dollar-linked products."
            )
        )
