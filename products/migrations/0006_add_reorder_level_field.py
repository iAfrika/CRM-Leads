from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_add_current_stock_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='reorder_level',
            field=models.PositiveIntegerField(default=5),
        ),
    ]