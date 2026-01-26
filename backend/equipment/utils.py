import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def parse_csv_file(file):
    """Parse uploaded CSV file and return DataFrame"""
    try:
        content = file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        required_cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
        
        df = df.dropna()
        return df
    except Exception as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")

def calculate_summary_stats(df):
    """Calculate summary statistics from DataFrame"""
    summary = {
        'total_count': len(df),
        'avg_flowrate': round(df['Flowrate'].mean(), 2),
        'avg_pressure': round(df['Pressure'].mean(), 2),
        'avg_temperature': round(df['Temperature'].mean(), 2),
        'min_flowrate': round(df['Flowrate'].min(), 2),
        'max_flowrate': round(df['Flowrate'].max(), 2),
        'min_pressure': round(df['Pressure'].min(), 2),
        'max_pressure': round(df['Pressure'].max(), 2),
        'min_temperature': round(df['Temperature'].min(), 2),
        'max_temperature': round(df['Temperature'].max(), 2),
        'equipment_types': df['Type'].value_counts().to_dict()
    }
    return summary

def generate_pdf_report(dataset, buffer):
    """Generate PDF report for a dataset"""
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title = Paragraph("Chemical Equipment Analysis Report", styles['Heading1'])
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    info = [
        Paragraph(f"<b>Filename:</b> {dataset.filename}", styles['Normal']),
        Paragraph(f"<b>Upload Date:</b> {dataset.upload_date.strftime('%Y-%m-%d %H:%M')}", styles['Normal']),
        Paragraph(f"<b>Total Records:</b> {dataset.row_count}", styles['Normal']),
    ]
    for item in info:
        story.append(item)
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.3*inch))
    
    summary = dataset.get_summary()
    summary_title = Paragraph("<b>Summary Statistics</b>", styles['Heading2'])
    story.append(summary_title)
    story.append(Spacer(1, 0.2*inch))
    
    summary_data = [
        ['Parameter', 'Average', 'Min', 'Max'],
        ['Flowrate', f"{summary['avg_flowrate']}", f"{summary['min_flowrate']}", f"{summary['max_flowrate']}"],
        ['Pressure', f"{summary['avg_pressure']}", f"{summary['min_pressure']}", f"{summary['max_pressure']}"],
        ['Temperature', f"{summary['avg_temperature']}", f"{summary['min_temperature']}", f"{summary['max_temperature']}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    types_title = Paragraph("<b>Equipment Type Distribution</b>", styles['Heading2'])
    story.append(types_title)
    story.append(Spacer(1, 0.2*inch))
    
    types_data = [['Equipment Type', 'Count']]
    for eq_type, count in summary['equipment_types'].items():
        types_data.append([eq_type, str(count)])
    
    types_table = Table(types_data, colWidths=[4*inch, 2*inch])
    types_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(types_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer