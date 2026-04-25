from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("promotions", "0002_promotion_badge_text_ar_promotion_cta_text_ar_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="promotion",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
