import django.db.models.deletion
import apps.catalog.models
from django.db import migrations, models


def migrate_product_companies(apps, schema_editor):
    Company = apps.get_model("catalog", "Company")
    ProductCompany = apps.get_model("catalog", "ProductCompany")
    companies_by_name = {}

    for product_company in ProductCompany.objects.all().iterator():
        name_key = (product_company.name or "").strip().casefold()
        company = companies_by_name.get(name_key)
        if company is None:
            company = Company.objects.create(
                code=f"legacy-{product_company.pk}",
                name=product_company.name,
                logo=product_company.logo,
                external_logo_url=product_company.external_logo_url,
                display_order=product_company.order,
                is_active=product_company.is_active,
            )
            companies_by_name[name_key] = company
        product_company.company = company
        product_company.save(update_fields=["company"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0011_productoption_is_available"),
    ]

    operations = [
        migrations.CreateModel(
            name="Company",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=120, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("logo", models.ImageField(blank=True, upload_to=apps.catalog.models.company_upload_path)),
                ("external_logo_url", models.URLField(blank=True)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name_plural": "Companies",
                "ordering": ["display_order", "name", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="company",
            index=models.Index(
                fields=["is_active", "display_order"],
                name="catalog_com_is_acti_a611d7_idx",
            ),
        ),
        migrations.AddField(
            model_name="productcompany",
            name="company",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="catalog.company",
            ),
        ),
        migrations.RunPython(migrate_product_companies, migrations.RunPython.noop),
        migrations.RemoveIndex(
            model_name="productcompany",
            name="catalog_pro_product_2630b6_idx",
        ),
        migrations.RemoveField(model_name="productcompany", name="external_logo_url"),
        migrations.RemoveField(model_name="productcompany", name="is_active"),
        migrations.RemoveField(model_name="productcompany", name="logo"),
        migrations.RemoveField(model_name="productcompany", name="name"),
        migrations.RemoveField(model_name="productcompany", name="order"),
        migrations.AlterField(
            model_name="productcompany",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="catalog.company",
            ),
        ),
        migrations.AlterModelOptions(
            name="productcompany",
            options={
                "ordering": ["company__display_order", "company__name", "id"],
                "verbose_name": "Product company",
                "verbose_name_plural": "Product companies",
            },
        ),
        migrations.AddConstraint(
            model_name="productcompany",
            constraint=models.UniqueConstraint(
                fields=("product", "company"),
                name="unique_product_company",
            ),
        ),
        migrations.AddIndex(
            model_name="productcompany",
            index=models.Index(
                fields=["product", "company"],
                name="catalog_pro_product_6a49de_idx",
            ),
        ),
    ]
