from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_deliverysubarea_customeraddress_sub_area"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliverysubarea",
            name="delivery_fee",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
