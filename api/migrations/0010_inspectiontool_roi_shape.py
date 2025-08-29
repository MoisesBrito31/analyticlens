from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_alter_toolkind_category_alter_toolkind_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspectiontool',
            name='roi_shape',
            field=models.JSONField(default=dict, blank=True, verbose_name='ROI (shape)'),
        ),
    ]


