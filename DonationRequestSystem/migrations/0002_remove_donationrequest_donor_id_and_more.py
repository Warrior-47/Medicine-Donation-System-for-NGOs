from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('DonationRequestSystem', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donationrequest',
            name='Donor_id',
        ),
        migrations.RemoveField(
            model_name='donationrequest',
            name='NGO_id',
        ),
        migrations.AddField(
            model_name='donationrequest',
            name='Donor',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='donor', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='donationrequest',
            name='NGO',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='ngo', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='donationrequest',
            name='Medicine_list',
            field=models.CharField(blank=True, max_length=25),
        ),
        migrations.CreateModel(
            name='donatedMedicines',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine_name', models.CharField(blank=True, max_length=100)),
                ('dosage_amount', models.IntegerField()),
                ('number_of_pills', models.IntegerField()),
                ('donation_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DonationRequestSystem.donationrequest')),
            ],
        ),
    ]
