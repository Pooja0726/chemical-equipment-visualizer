from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import FileResponse
from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import Dataset, EquipmentRecord
from .serializers import DatasetSerializer, DatasetDetailSerializer, EquipmentRecordSerializer
from .utils import parse_csv_file, calculate_summary_stats, generate_pdf_report
import io
import traceback

class DatasetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing datasets"""
    queryset = Dataset.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DatasetDetailSerializer
        return DatasetSerializer
    
    def get_queryset(self):
        """Return datasets based on action"""
        if self.action == 'list':
            return Dataset.objects.all().order_by('-id')[:5]
        return Dataset.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to handle non-existent datasets gracefully"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception:
            return Response(
                {
                    'error': 'Dataset not found or has been deleted',
                    'message': 'Please refresh the dataset list'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload and process CSV file"""
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        if not file.name.endswith('.csv'):
            return Response(
                {'error': 'Only CSV files are allowed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Step 1: Parsing CSV
            df = parse_csv_file(file)
            
            # Step 2: Calculating summary statistics
            summary = calculate_summary_stats(df)
            
            # Step 3: Maintaining last 5 datasets
            old_datasets = Dataset.objects.all().order_by('-id')[4:]
            for old in old_datasets:
                old.delete()
            
            # Step 4: Creating dataset in database
            # This direct creation bypasses the Serializer "required field" errors
            dataset = Dataset.objects.create(
                filename=file.name,
                row_count=len(df)
            )
            dataset.set_summary(summary)
            dataset.save()
            
            # Step 5: Creating equipment records
            records = []
            for _, row in df.iterrows():
                records.append(EquipmentRecord(
                    dataset=dataset,
                    equipment_name=row.get('Equipment Name', 'N/A'),
                    equipment_type=row.get('Type', 'N/A'),
                    flowrate=row.get('Flowrate', 0),
                    pressure=row.get('Pressure', 0),
                    temperature=row.get('Temperature', 0)
                ))
            
            EquipmentRecord.objects.bulk_create(records)
            
            # Step 6: Serializing response
            serializer = DatasetDetailSerializer(dataset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Generate and download PDF report"""
        dataset = get_object_or_404(Dataset, pk=pk)
        
        buffer = io.BytesIO()
        generate_pdf_report(dataset, buffer)
        buffer.seek(0)
        
        response = FileResponse(
            buffer, 
            as_attachment=True, 
            filename=f'report_{dataset.id}.pdf',
            content_type='application/pdf'
        )
        return response
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get overall statistics"""
        total_datasets = Dataset.objects.count()
        total_records = EquipmentRecord.objects.count()
        
        # Type distribution across all datasets
        type_counts = list(EquipmentRecord.objects.values('equipment_type').annotate(
            count=Count('equipment_type')
        ).order_by('-count'))
        
        return Response({
            'total_datasets': total_datasets,
            'total_records': total_records,
            'type_distribution': type_counts
        })