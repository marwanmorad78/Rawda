from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_deliveryarea_has_sub_areas"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerorderitem",
            name="cart_item_id",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
