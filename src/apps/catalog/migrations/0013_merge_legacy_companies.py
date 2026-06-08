from django.db import migrations


def merge_product_company(apps, source_relation, target_relation):
    ProductCompanyOption = apps.get_model("catalog", "ProductCompanyOption")
    CustomerOrderItem = apps.get_model("core", "CustomerOrderItem")

    for source_option in ProductCompanyOption.objects.filter(company=source_relation).iterator():
        target_option = (
            ProductCompanyOption.objects.filter(
                company=target_relation,
                name__iexact=source_option.name,
            )
            .order_by("id")
            .first()
        )
        if target_option is None:
            source_option.company = target_relation
            source_option.save(update_fields=["company"])
        else:
            CustomerOrderItem.objects.filter(selected_option=source_option).update(
                selected_option=target_option
            )
            source_option.delete()

    CustomerOrderItem.objects.filter(company=source_relation).update(company=target_relation)
    source_relation.delete()


def merge_legacy_companies(apps, schema_editor):
    Company = apps.get_model("catalog", "Company")
    ProductCompany = apps.get_model("catalog", "ProductCompany")

    canonical_by_name = {}
    duplicate_canonical_names = set()
    for company in Company.objects.exclude(code__startswith="legacy-").iterator():
        name_key = (company.name or "").strip().casefold()
        if name_key in canonical_by_name:
            duplicate_canonical_names.add(name_key)
        else:
            canonical_by_name[name_key] = company

    for legacy_company in Company.objects.filter(code__startswith="legacy-").iterator():
        name_key = (legacy_company.name or "").strip().casefold()
        if name_key in duplicate_canonical_names:
            continue
        canonical_company = canonical_by_name.get(name_key)
        if canonical_company is None:
            continue

        if not canonical_company.logo and legacy_company.logo:
            canonical_company.logo = legacy_company.logo
        if not canonical_company.external_logo_url and legacy_company.external_logo_url:
            canonical_company.external_logo_url = legacy_company.external_logo_url
        canonical_company.save(update_fields=["logo", "external_logo_url", "updated_at"])

        for source_relation in ProductCompany.objects.filter(company=legacy_company).iterator():
            target_relation = ProductCompany.objects.filter(
                product_id=source_relation.product_id,
                company=canonical_company,
            ).first()
            if target_relation is None:
                source_relation.company = canonical_company
                source_relation.save(update_fields=["company"])
            else:
                merge_product_company(apps, source_relation, target_relation)

        legacy_company.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0012_global_company"),
        ("core", "0017_alter_customerorderitem_quantity"),
    ]

    operations = [
        migrations.RunPython(merge_legacy_companies, migrations.RunPython.noop),
    ]
