from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_inspection_reference_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspection',
            name='reference_image_path',
            field=models.CharField(max_length=500, null=True, blank=True, verbose_name='Caminho da Imagem de Referência'),
        ),
        migrations.RemoveField(
            model_name='inspection',
            name='reference_image_base64',
        ),
    ]


