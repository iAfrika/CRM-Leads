from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_add_selling_price_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='current_stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]