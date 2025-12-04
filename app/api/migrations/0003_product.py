from decimal import Decimal
import uuid
from django.db import migrations, models


def create_initial_products(apps, schema_editor):
    Product = apps.get_model("api", "Product")
    products = [
        {"name": "krokumbush", "price": Decimal("450")},
        {"name": "saint-honore", "price": Decimal("250")},
        {"name": "millioner cookie(10)", "price": Decimal("200")},
        {"name": "pavlova", "price": Decimal("200")},
        {"name": "designed cake", "price": Decimal("250")},
    ]

    Product.objects.bulk_create([Product(**product) for product in products])


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_order"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.RunPython(create_initial_products, migrations.RunPython.noop),
    ]
