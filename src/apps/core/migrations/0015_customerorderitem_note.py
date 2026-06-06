from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_order_item_company_selection"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerorderitem",
            name="note",
            field=models.TextField(blank=True),
        ),
    ]
