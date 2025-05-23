# Generated by Django 5.2 on 2025-05-01 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agrobuild', '0006_delete_logindata'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='P_img',
            field=models.ImageField(default='', upload_to='image/img'),
        ),
        migrations.AlterField(
            model_name='product',
            name='P_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
