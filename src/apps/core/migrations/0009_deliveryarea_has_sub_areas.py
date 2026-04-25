from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_deliverysubarea_delivery_fee"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliveryarea",
            name="has_sub_areas",
            field=models.BooleanField(default=False),
        ),
    ]
