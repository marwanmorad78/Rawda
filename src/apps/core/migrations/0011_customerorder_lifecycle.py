from django.db import migrations, models


def migrate_order_statuses(apps, schema_editor):
    CustomerOrder = apps.get_model("core", "CustomerOrder")
    CustomerOrder.objects.filter(status="confirmed").update(status="done")
    CustomerOrder.objects.filter(status="pending").update(status="waiting_accept")


def revert_order_statuses(apps, schema_editor):
    CustomerOrder = apps.get_model("core", "CustomerOrder")
    CustomerOrder.objects.filter(status="done").update(status="confirmed")
    CustomerOrder.objects.filter(
        status__in=["waiting_accept", "being_prepared", "out_for_delivery", "ready_to_pickup", "cancelled"]
    ).update(status="pending")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_customerorderitem_cart_item_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customerorder",
            name="status",
            field=models.CharField(
                choices=[
                    ("waiting_accept", "Waiting for accept"),
                    ("being_prepared", "Being prepared"),
                    ("out_for_delivery", "Out for delivery"),
                    ("ready_to_pickup", "Ready to pick up"),
                    ("done", "Done"),
                    ("cancelled", "Cancelled"),
                ],
                default="waiting_accept",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="customerorder",
            name="expected_time_minutes",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="customerorder",
            name="accepted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="customerorder",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_order_statuses, revert_order_statuses),
    ]
