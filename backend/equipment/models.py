from django.db import models
from django.contrib.auth.models import User
import json

class Dataset(models.Model):
    """Store uploaded datasets with metadata"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField()
    summary_stats = models.TextField()  # JSON string
    
    class Meta:
        ordering = ['-upload_date']
    
    def get_summary(self):
        """Parse JSON summary stats"""
        return json.loads(self.summary_stats)
    
    def set_summary(self, data):
        """Set summary stats from dict"""
        self.summary_stats = json.dumps(data)
    
    def __str__(self):
        return f"{self.filename} - {self.upload_date.strftime('%Y-%m-%d %H:%M')}"


class EquipmentRecord(models.Model):
    """Store individual equipment records"""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='records')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"