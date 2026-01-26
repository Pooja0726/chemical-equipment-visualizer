from rest_framework import serializers
from .models import Dataset, EquipmentRecord

class EquipmentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentRecord
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class DatasetSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'upload_date', 'row_count', 'summary']
    
    def get_summary(self, obj):
        return obj.get_summary()


class DatasetDetailSerializer(serializers.ModelSerializer):
    records = EquipmentRecordSerializer(many=True, read_only=True)
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'upload_date', 'row_count', 'summary', 'records']
    
    def get_summary(self, obj):
        return obj.get_summary()