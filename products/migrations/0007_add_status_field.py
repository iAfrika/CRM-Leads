from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_add_reorder_level_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('discontinued', 'Discontinued'), ('out_of_stock', 'Out of Stock')], default='active', max_length=20),
        ),
    ]