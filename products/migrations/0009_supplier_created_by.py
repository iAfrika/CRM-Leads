from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('products', '0008_add_created_by_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='product_suppliers',
                to='auth.user'
            ),
        ),
    ]