# Generated by Django 4.0.2 on 2022-06-09 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0005_alter_post_sub_title_alter_post_thumbnail_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='work',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contents.work'),
        ),
    ]