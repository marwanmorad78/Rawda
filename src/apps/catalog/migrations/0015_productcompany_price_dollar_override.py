from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0014_alter_category_cover_image_alter_company_logo_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productcompany",
            name="is_price_linked_to_dollar",
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
