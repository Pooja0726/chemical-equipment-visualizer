from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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
    permission_classes = [AllowAny]  # Change to [IsAuthenticated] for auth
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DatasetDetailSerializer
        return DatasetSerializer
    
    def get_queryset(self):
        """Return datasets based on action"""
        # For list action, return last 5 datasets
        if self.action == 'list':
            return Dataset.objects.all().order_by('-id')[:5]
        # For other actions (retrieve, update, delete), return all datasets
        return Dataset.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to handle non-existent datasets gracefully"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Dataset.DoesNotExist:
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
        print("\n" + "="*60)
        print("🔵 UPLOAD REQUEST RECEIVED")
        print("="*60)
        
        # Debug: Check what's in the request
        print(f"📋 Request FILES keys: {list(request.FILES.keys())}")
        print(f"📋 Request DATA keys: {list(request.data.keys())}")
        
        if 'file' not in request.FILES:
            print("❌ ERROR: 'file' not found in request.FILES")
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        print(f"✅ File received: {file.name}")
        print(f"📊 File size: {file.size} bytes")
        
        # Validate file extension
        if not file.name.endswith('.csv'):
            print(f"❌ ERROR: Invalid file extension")
            return Response(
                {'error': 'Only CSV files are allowed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print("✅ File extension validated (.csv)")
        
        try:
            print("\n🔄 Step 1: Parsing CSV...")
            df = parse_csv_file(file)
            print(f"✅ CSV parsed successfully!")
            print(f"   - Rows: {len(df)}")
            print(f"   - Columns: {list(df.columns)}")
            
            print("\n🔄 Step 2: Calculating summary statistics...")
            summary = calculate_summary_stats(df)
            print(f"✅ Summary calculated!")
            print(f"   - Average Flowrate: {summary['avg_flowrate']}")
            print(f"   - Average Pressure: {summary['avg_pressure']}")
            print(f"   - Average Temperature: {summary['avg_temperature']}")
            
            print("\n🔄 Step 3: Maintaining last 5 datasets (delete old ones first)...")
            # Delete old datasets BEFORE creating new one
            old_datasets = Dataset.objects.all().order_by('-id')[4:]  # Keep only latest 4
            deleted_count = len(old_datasets)
            deleted_ids = [ds.id for ds in old_datasets]
            for old in old_datasets:
                old.delete()
            print(f"✅ Deleted {deleted_count} old datasets (IDs: {deleted_ids})")
            
            print("\n🔄 Step 4: Creating dataset in database...")
            dataset = Dataset.objects.create(
                filename=file.name,
                row_count=len(df)
            )
            dataset.set_summary(summary)
            dataset.save()
            print(f"✅ Dataset created! ID: {dataset.id}")
            
            print("\n🔄 Step 5: Creating equipment records...")
            records = []
            for idx, row in df.iterrows():
                records.append(EquipmentRecord(
                    dataset=dataset,
                    equipment_name=row['Equipment Name'],
                    equipment_type=row['Type'],
                    flowrate=row['Flowrate'],
                    pressure=row['Pressure'],
                    temperature=row['Temperature']
                ))
            
            EquipmentRecord.objects.bulk_create(records)
            print(f"✅ Created {len(records)} equipment records!")
            
            print("\n🔄 Step 6: Serializing response...")
            serializer = DatasetDetailSerializer(dataset)
            
            print("\n" + "="*60)
            print("🎉 UPLOAD SUCCESSFUL!")
            print("="*60 + "\n")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print("\n" + "="*60)
            print("❌ ERROR OCCURRED DURING UPLOAD")
            print("="*60)
            print(f"\n🔴 Error Type: {type(e).__name__}")
            print(f"🔴 Error Message: {str(e)}")
            print("\n📋 Full Traceback:")
            print(traceback.format_exc())
            print("="*60 + "\n")
            
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Generate and download PDF report"""
        try:
            dataset = self.get_object()
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found or has been deleted'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        buffer = io.BytesIO()
        generate_pdf_report(dataset, buffer)
        
        response = FileResponse(
            buffer, 
            as_attachment=True, 
            filename=f'report_{dataset.filename}_{dataset.id}.pdf',
            content_type='application/pdf'
        )
        return response
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get overall statistics"""
        total_datasets = Dataset.objects.count()
        total_records = EquipmentRecord.objects.count()
        
        # Type distribution across all datasets
        type_counts = EquipmentRecord.objects.values('equipment_type').annotate(
            count=Count('equipment_type')
        ).order_by('-count')
        
        return Response({
            'total_datasets': total_datasets,
            'total_records': total_records,
            'type_distribution': list(type_counts)
        })