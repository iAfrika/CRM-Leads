from django.db import migrations, models
import uuid

def generate_item_code():
    return f"PROD-{uuid.uuid4().hex[:8].upper()}"

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='sku',
        ),
        migrations.AddField(
            model_name='product',
            name='item_code',
            field=models.CharField(default=generate_item_code, max_length=50, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]