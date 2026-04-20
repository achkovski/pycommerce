from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_sitesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_digital',
            field=models.BooleanField(
                default=False,
                help_text='Products in this category are digital downloads — excluded from the shop listings and shown on the Downloads page instead',
            ),
        ),
    ]
