from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.catalog.models import Category, Product
from apps.core.models import SiteSettings
from apps.promotions.models import Promotion


class Command(BaseCommand):
    help = "Seed the storefront with bilingual categories, products, and promotions."

    def handle(self, *args, **options):
        site_settings, _ = SiteSettings.objects.update_or_create(
            pk=1,
            defaults={
                "store_name": "Al Rawda Center",
                "store_name_ar": "مركز الروضة",
                "tagline": "All you need to cook",
                "tagline_ar": "كل ما تحتاجه للطبخ",
                "about_text": "Al Rawda Center is a neighborhood grocery destination focused on fresh produce, pantry staples, juices, legumes, and frozen essentials.",
                "about_text_ar": "مركز الروضة وجهة بقالة محلية تهتم بالخضار والفواكه الطازجة والمواد التموينية والعصائر والبقوليات والمنتجات المجمدة.",
                "address": "Main Market Street, Damascus",
                "address_ar": "الشارع التجاري الرئيسي، دمشق",
                "primary_phone": "+963-11-555-1000",
                "secondary_phone": "+963-944-000-111",
                "email": "info@alrawdacenter.com",
                "working_hours_summary": "Daily from 8:00 AM to 10:00 PM",
                "working_hours_summary_ar": "يومياً من 8:00 صباحاً حتى 10:00 مساءً",
                "hero_title": "Fresh choices for every kitchen",
                "hero_title_ar": "خيارات طازجة لكل مطبخ",
                "hero_subtitle": "Browse vegetables, fruits, juices, canned food, legumes, and frozen products with prices updated by the store team.",
                "hero_subtitle_ar": "تصفح الخضار والفواكه والعصائر والمعلبات والبقوليات والمنتجات المجمدة مع أسعار محدثة من فريق المتجر.",
                "hero_cta_text": "Browse categories",
                "hero_cta_text_ar": "تصفح الأقسام",
                "hero_cta_url": "/#categories",
                "is_active": True,
            },
        )

        category_data = [
            {
                "slug": "vegetables",
                "name": "Vegetables",
                "name_ar": "الخضار",
                "description": "Fresh vegetables for daily cooking.",
                "description_ar": "خضار طازجة للطبخ اليومي.",
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Local%20tomatoes.jpg",
                "display_order": 1,
            },
            {
                "slug": "fruits",
                "name": "Fruits",
                "name_ar": "الفواكه",
                "description": "Seasonal and imported fruits.",
                "description_ar": "فواكه موسمية ومستوردات مختارة.",
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Bananas%20white%20background.jpg",
                "display_order": 2,
            },
            {
                "slug": "juices",
                "name": "Juices",
                "name_ar": "العصائر",
                "description": "Refreshing bottled and chilled juices.",
                "description_ar": "عصائر منعشة ومبردة ومعبأة.",
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Orange%20juice%200001.jpg",
                "display_order": 3,
            },
            {
                "slug": "canned-food",
                "name": "Canned Food",
                "name_ar": "المعلبات",
                "description": "Pantry staples and preserved foods.",
                "description_ar": "مواد تموينية ومعلبات أساسية للمطبخ.",
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Canned%20food.jpg",
                "display_order": 4,
            },
            {
                "slug": "legumes",
                "name": "Legumes",
                "name_ar": "البقوليات",
                "description": "Beans, lentils, chickpeas, and more.",
                "description_ar": "عدس وحمص وفاصولياء وبقوليات متنوعة.",
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Dried%20Green%20Peas.jpg",
                "display_order": 5,
            },
            {
                "slug": "frozen-products",
                "name": "Frozen Products",
                "name_ar": "المجمدات",
                "description": "Frozen vegetables and ready-to-cook essentials.",
                "description_ar": "خضار مجمدة ومنتجات جاهزة للطبخ.",
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Peas%20and%20carrots%20%2819675818713%29.jpg",
                "display_order": 6,
            },
        ]

        categories = {}
        for item in category_data:
            category, _ = Category.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "name_ar": item["name_ar"],
                    "description": item["description"],
                    "description_ar": item["description_ar"],
                    "display_order": item["display_order"],
                    "is_active": True,
                    "external_image_url": item["external_image_url"],
                },
            )
            categories[item["slug"]] = category

        product_data = [
            {
                "category": "vegetables",
                "name": "Tomatoes",
                "name_ar": "بندورة",
                "slug": "tomatoes",
                "short_description": "Fresh red tomatoes for salads and cooking.",
                "short_description_ar": "بندورة حمراء طازجة للسلطات والطبخ.",
                "description": "Juicy tomatoes selected for everyday kitchen use.",
                "description_ar": "بندورة غنية بالعصارة ومناسبة للاستخدام اليومي في المطبخ.",
                "price": "8500",
                "unit_label": "per kg",
                "unit_label_ar": "للكيلو",
                "sku": "VEG-TOM-001",
                "is_featured": True,
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Local%20tomatoes.jpg",
            },
            {
                "category": "fruits",
                "name": "Bananas",
                "name_ar": "موز",
                "slug": "bananas",
                "short_description": "Sweet ripe bananas.",
                "short_description_ar": "موز ناضج وحلو.",
                "description": "A reliable fresh fruit choice for breakfast and snacks.",
                "description_ar": "خيار فاكهة طازج ومناسب للفطور والوجبات الخفيفة.",
                "price": "12000",
                "unit_label": "per kg",
                "unit_label_ar": "للكيلو",
                "sku": "FRU-BAN-001",
                "is_featured": True,
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Bananas%20white%20background.jpg",
            },
            {
                "category": "juices",
                "name": "Orange Juice",
                "name_ar": "عصير برتقال",
                "slug": "orange-juice",
                "short_description": "Chilled citrus juice bottle.",
                "short_description_ar": "عبوة عصير حمضيات مبردة.",
                "description": "Refreshing orange juice for family meals and quick refreshment.",
                "description_ar": "عصير برتقال منعش مناسب للوجبات العائلية والانتعاش السريع.",
                "price": "9000",
                "unit_label": "per bottle",
                "unit_label_ar": "للعبوة",
                "sku": "JUI-ORA-001",
                "is_featured": True,
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Orange%20juice%200001.jpg",
            },
            {
                "category": "canned-food",
                "name": "Canned Corn",
                "name_ar": "ذرة معلبة",
                "slug": "canned-corn",
                "short_description": "Easy pantry staple for quick meals.",
                "short_description_ar": "مكون أساسي سهل للوجبات السريعة.",
                "description": "Convenient canned corn to keep the kitchen stocked.",
                "description_ar": "ذرة معلبة عملية لإبقاء المطبخ مجهزاً دائماً.",
                "price": "6500",
                "unit_label": "per can",
                "unit_label_ar": "للعلبة",
                "sku": "CAN-COR-001",
                "is_featured": False,
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Canned%20food.jpg",
            },
            {
                "category": "legumes",
                "name": "Green Peas",
                "name_ar": "بازلاء",
                "slug": "green-peas",
                "short_description": "Quality dried green peas.",
                "short_description_ar": "بازلاء يابسة عالية الجودة.",
                "description": "A dependable legumes option for soups and home cooking.",
                "description_ar": "خيار بقوليات ممتاز للشوربات والطبخ المنزلي.",
                "price": "7000",
                "unit_label": "per kg",
                "unit_label_ar": "للكيلو",
                "sku": "LEG-PEA-001",
                "is_featured": True,
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Dried%20Green%20Peas.jpg",
            },
            {
                "category": "frozen-products",
                "name": "Frozen Peas & Carrots",
                "name_ar": "بازلاء وجزر مجمد",
                "slug": "frozen-peas-carrots",
                "short_description": "Ready-to-cook mixed vegetables.",
                "short_description_ar": "خضار مشكلة جاهزة للطبخ.",
                "description": "A convenient frozen mix for rice dishes, soups, and quick meals.",
                "description_ar": "خليط مجمد مناسب للأرز والشوربات والوجبات السريعة.",
                "price": "11000",
                "unit_label": "per bag",
                "unit_label_ar": "للكيس",
                "sku": "FRO-PEA-001",
                "is_featured": True,
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Peas%20and%20carrots%20%2819675818713%29.jpg",
            },
        ]

        for item in product_data:
            Product.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "category": categories[item["category"]],
                    "name": item["name"],
                    "name_ar": item["name_ar"],
                    "short_description": item["short_description"],
                    "short_description_ar": item["short_description_ar"],
                    "description": item["description"],
                    "description_ar": item["description_ar"],
                    "price": item["price"],
                    "unit_label": item["unit_label"],
                    "unit_label_ar": item["unit_label_ar"],
                    "is_available": True,
                    "is_featured": item["is_featured"],
                    "sku": item["sku"],
                    "external_image_url": item["external_image_url"],
                },
            )

        today = timezone.localdate()
        Promotion.objects.update_or_create(
            slug="weekly-fresh-deals",
            defaults={
                "title": "Weekly Fresh Deals",
                "title_ar": "عروض الأسبوع الطازجة",
                "subtitle": "Special prices across produce and essentials",
                "subtitle_ar": "أسعار مميزة على الخضار والمواد الأساسية",
                "description": "A rotating set of fresh and pantry offers curated for everyday shopping.",
                "description_ar": "مجموعة متجددة من العروض على المنتجات الطازجة والمواد التموينية للتسوق اليومي.",
                "badge_text": "Limited Offer",
                "badge_text_ar": "عرض محدود",
                "cta_text": "Browse categories",
                "cta_text_ar": "تصفح الأقسام",
                "cta_url": "/#categories",
                "external_image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Canned%20food.jpg",
                "is_active": True,
                "display_order": 1,
                "start_date": today,
                "end_date": today + timedelta(days=30),
            },
        )

        self.stdout.write(self.style.SUCCESS("Storefront seed data created successfully."))
