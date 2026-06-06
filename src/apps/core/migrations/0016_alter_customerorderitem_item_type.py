from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_customerorderitem_note"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customerorderitem",
            name="item_type",
            field=models.CharField(max_length=32),
        ),
    ]
