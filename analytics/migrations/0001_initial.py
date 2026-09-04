from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial=True
    dependencies=[('events','0001_initial')]
    operations=[
        migrations.CreateModel(name='Anomaly',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('event_type',models.CharField(db_index=True,max_length=100)),
            ('score',models.FloatField(help_text='Isolation Forest anomaly score (lower = more anomalous).')),
            ('reason',models.CharField(blank=True,default='',max_length=255)),
            ('detected_at',models.DateTimeField(auto_now_add=True)),
            ('event',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='anomalies',to='events.event'))],
            options={'ordering':['-detected_at']}),
        migrations.CreateModel(name='Forecast',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('event_type',models.CharField(db_index=True,max_length=100)),
            ('predicted_value',models.FloatField()),
            ('horizon_minutes',models.IntegerField(default=5)),
            ('based_on_samples',models.IntegerField(default=0)),
            ('created_at',models.DateTimeField(auto_now_add=True))],
            options={'ordering':['-created_at']})
    ]
