from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_toolkind_inspection_inspectiontool_grayscaletool_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspection',
            name='reference_image_base64',
            field=models.TextField(blank=True, null=True, verbose_name='Imagem de Referência (Base64)'),
        ),
        migrations.AddField(
            model_name='inspection',
            name='reference_image_mime',
            field=models.CharField(max_length=50, blank=True, null=True, verbose_name='MIME da Imagem de Referência'),
        ),
        migrations.AddField(
            model_name='inspection',
            name='reference_image_width',
            field=models.IntegerField(blank=True, null=True, verbose_name='Largura da Imagem de Referência'),
        ),
        migrations.AddField(
            model_name='inspection',
            name='reference_image_height',
            field=models.IntegerField(blank=True, null=True, verbose_name='Altura da Imagem de Referência'),
        ),
    ]


