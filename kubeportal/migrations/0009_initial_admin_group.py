# Generated by Django 2.2.16 on 2021-02-20 21:53

from django.db import migrations


def add_admin_group(apps, schema_editor):
    # We can't import the model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    PortalGroup = apps.get_model('kubeportal', 'PortalGroup')
    has_admin_group = PortalGroup.objects.filter(can_admin=True).exists()
    if not has_admin_group:
        admin_group = PortalGroup(name="Admin users", can_admin=True)
        admin_group.save()



class Migration(migrations.Migration):

    dependencies = [
        ('kubeportal', '0008_user_alt_mails'),
    ]

    operations = [
        migrations.RunPython(add_admin_group),
    ]

