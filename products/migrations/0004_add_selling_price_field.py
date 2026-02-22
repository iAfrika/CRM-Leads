from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_add_buying_price_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='selling_price',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
            preserve_default=False,
        ),
    ]