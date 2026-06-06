from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_alter_customerorderitem_item_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customerorderitem",
            name="quantity",
            field=models.DecimalField(decimal_places=1, default=1, max_digits=10),
        ),
    ]
