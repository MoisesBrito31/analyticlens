from django.db import migrations, models


def seed_tool_kinds(apps, schema_editor):
    ToolKind = apps.get_model('api', 'ToolKind')
    defaults = [
        {
            'slug': 'grayscale',
            'label': 'Grayscale',
            'category': 'filter',
            'description': 'Conversão para escala de cinza (filtro)'
        },
        {
            'slug': 'blur',
            'label': 'Blur',
            'category': 'filter',
            'description': 'Suavização da imagem (gaussian/median)'
        },
        {
            'slug': 'threshold',
            'label': 'Threshold',
            'category': 'filter',
            'description': 'Binarização (binary/range/otsu)'
        },
        {
            'slug': 'morphology',
            'label': 'Morphology',
            'category': 'filter',
            'description': 'Abertura/Fechamento para limpeza e suavização'
        },
        {
            'slug': 'blob',
            'label': 'Blob',
            'category': 'analytic',
            'description': 'Detecção e análise de blobs (analítica)'
        },
        {
            'slug': 'math',
            'label': 'Math',
            'category': 'math',
            'description': 'Operações matemáticas sobre resultados (ex.: area_ratio)'
        },
    ]

    for data in defaults:
        ToolKind.objects.update_or_create(slug=data['slug'], defaults=data)


def unseed_tool_kinds(apps, schema_editor):
    ToolKind = apps.get_model('api', 'ToolKind')
    ToolKind.objects.filter(slug__in=['grayscale', 'blur', 'threshold', 'morphology', 'blob', 'math']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_virtualmachine_django_url_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolKind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=50, unique=True, verbose_name='Slug')),
                ('label', models.CharField(max_length=100, verbose_name='Rótulo')),
                ('category', models.CharField(max_length=20, verbose_name='Categoria')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Tipo de Tool',
                'verbose_name_plural': 'Tipos de Tools',
                'ordering': ['slug'],
            },
        ),
        migrations.RunPython(seed_tool_kinds, unseed_tool_kinds),
    ]


