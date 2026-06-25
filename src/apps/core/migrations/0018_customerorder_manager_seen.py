from django.db import migrations, models


def mark_existing_orders_seen(apps, schema_editor):
    CustomerOrder = apps.get_model("core", "CustomerOrder")
    CustomerOrder.objects.update(manager_seen=True)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_alter_customerorderitem_quantity"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerorder",
            name="manager_seen",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(mark_existing_orders_seen, migrations.RunPython.noop),
    ]
