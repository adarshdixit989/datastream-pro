from django.db import migrations, models

class Migration(migrations.Migration):
    initial=True
    dependencies=[]
    operations=[migrations.CreateModel(name='Event',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('event_type',models.CharField(db_index=True,max_length=100)),
        ('source',models.CharField(default='unknown',max_length=100)),
        ('value',models.FloatField(help_text='Primary numeric metric for this event (e.g. amount, latency, count).')),
        ('payload',models.JSONField(blank=True,default=dict)),
        ('created_at',models.DateTimeField(auto_now_add=True,db_index=True)),
        ('published_to_kafka',models.BooleanField(default=False)),
    ],options={'ordering':['-created_at']}) ,
    migrations.AddIndex(model_name='event',index=models.Index(fields=['event_type','created_at'],name='events_even_event_t_3e0e72_idx'))]
