from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_delivery_areas_and_pickup_delivery"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliverySubArea",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=150)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sub_areas",
                        to="core.deliveryarea",
                    ),
                ),
            ],
            options={
                "ordering": ["display_order", "name"],
                "unique_together": {("area", "name")},
            },
        ),
        migrations.AddField(
            model_name="customeraddress",
            name="sub_area",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="addresses",
                to="core.deliverysubarea",
            ),
        ),
        migrations.AddIndex(
            model_name="deliverysubarea",
            index=models.Index(fields=["area", "is_active", "display_order"], name="core_delive_area_id_ad7854_idx"),
        ),
    ]
