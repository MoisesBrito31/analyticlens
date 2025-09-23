from django.db import migrations


def seed_locate_toolkind(apps, schema_editor):
    ToolKind = apps.get_model('api', 'ToolKind')
    data = {
        'slug': 'locate',
        'label': 'Locate',
        'category': 'analytic',
        'description': 'Localização de borda ao longo de uma seta (medição de x,y,ângulo)'
    }
    ToolKind.objects.update_or_create(slug=data['slug'], defaults=data)


def unseed_locate_toolkind(apps, schema_editor):
    ToolKind = apps.get_model('api', 'ToolKind')
    ToolKind.objects.filter(slug='locate').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_rename_th_min_locatetoolconfig_threshold_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_locate_toolkind, unseed_locate_toolkind),
    ]


