"""
Report Generation Routes - PDF, Excel, CSV exports
"""
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from app.models import Dataset, MiningResult, ActivityLog
from app import db
import pandas as pd
import json
import os
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
def index():
    """Report generation page"""
    results = MiningResult.query.join(Dataset).filter(
        Dataset.user_id == current_user.id
    ).order_by(MiningResult.created_at.desc()).all()
    return render_template('reports/index.html', results=results)


@reports_bp.route('/generate/csv/<int:result_id>')
@login_required
def generate_csv(result_id):
    """Generate CSV report"""
    result = MiningResult.query.get_or_404(result_id)
    dataset = Dataset.query.get(result.dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('reports.index'))

    reports_dir = current_app.config['REPORTS_FOLDER']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if result.rules_json:
        rules = json.loads(result.rules_json)
        df_rules = pd.DataFrame(rules)
        filepath = os.path.join(reports_dir, f'rules_report_{timestamp}.csv')
        df_rules.to_csv(filepath, index=False)

        log = ActivityLog(user_id=current_user.id, action='Export CSV',
                          details=f'Exported rules for {dataset.name}')
        db.session.add(log)
        db.session.commit()

        return send_file(filepath, as_attachment=True,
                         download_name=f'association_rules_{dataset.name}.csv')

    flash('No rules data available.', 'warning')
    return redirect(url_for('reports.index'))


@reports_bp.route('/generate/excel/<int:result_id>')
@login_required
def generate_excel(result_id):
    """Generate Excel report"""
    result = MiningResult.query.get_or_404(result_id)
    dataset = Dataset.query.get(result.dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('reports.index'))

    reports_dir = current_app.config['REPORTS_FOLDER']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(reports_dir, f'report_{timestamp}.xlsx')

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Sheet 1: Dataset Summary
        summary_data = {
            'Metric': ['Dataset Name', 'Algorithm', 'Min Support', 'Min Confidence',
                       'Min Lift', 'Frequent Itemsets', 'Association Rules', 'Generated'],
            'Value': [dataset.name, result.algorithm.upper(), result.min_support,
                      result.min_confidence, result.min_lift,
                      result.num_frequent_itemsets, result.num_rules,
                      result.created_at.strftime('%Y-%m-%d %H:%M')]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

        # Sheet 2: Frequent Itemsets
        if result.frequent_itemsets_json:
            itemsets = json.loads(result.frequent_itemsets_json)
            pd.DataFrame(itemsets).to_excel(writer, sheet_name='Frequent Itemsets', index=False)

        # Sheet 3: Association Rules
        if result.rules_json:
            rules = json.loads(result.rules_json)
            pd.DataFrame(rules).to_excel(writer, sheet_name='Association Rules', index=False)

        # Sheet 4: Original Dataset
        df_original = pd.read_csv(dataset.filepath)
        df_original.to_excel(writer, sheet_name='Dataset', index=False)

    log = ActivityLog(user_id=current_user.id, action='Export Excel',
                      details=f'Exported full report for {dataset.name}')
    db.session.add(log)
    db.session.commit()

    return send_file(filepath, as_attachment=True,
                     download_name=f'ARM_Report_{dataset.name}.xlsx')


@reports_bp.route('/generate/pdf/<int:result_id>')
@login_required
def generate_pdf(result_id):
    """Generate PDF report"""
    result = MiningResult.query.get_or_404(result_id)
    dataset = Dataset.query.get(result.dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('reports.index'))

    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch

        reports_dir = current_app.config['REPORTS_FOLDER']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(reports_dir, f'report_{timestamp}.pdf')

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=18)
        elements.append(Paragraph("Association Rule Mining Report", title_style))
        elements.append(Spacer(1, 20))

        # Summary
        elements.append(Paragraph(f"<b>Dataset:</b> {dataset.name}", styles['Normal']))
        elements.append(Paragraph(f"<b>Algorithm:</b> {result.algorithm.upper()}", styles['Normal']))
        elements.append(Paragraph(f"<b>Min Support:</b> {result.min_support}", styles['Normal']))
        elements.append(Paragraph(f"<b>Min Confidence:</b> {result.min_confidence}", styles['Normal']))
        elements.append(Paragraph(f"<b>Frequent Itemsets:</b> {result.num_frequent_itemsets}", styles['Normal']))
        elements.append(Paragraph(f"<b>Association Rules:</b> {result.num_rules}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Rules Table
        if result.rules_json:
            rules = json.loads(result.rules_json)
            elements.append(Paragraph("<b>Top Association Rules</b>", styles['Heading2']))
            elements.append(Spacer(1, 10))

            table_data = [['Antecedent', 'Consequent', 'Support', 'Confidence', 'Lift']]
            for rule in rules[:15]:
                table_data.append([
                    rule['antecedents'], rule['consequents'],
                    f"{rule['support']:.4f}", f"{rule['confidence']:.4f}",
                    f"{rule['lift']:.4f}"
                ])

            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E3F2FD')])
            ]))
            elements.append(table)

        doc.build(elements)

        log = ActivityLog(user_id=current_user.id, action='Export PDF',
                          details=f'Exported PDF for {dataset.name}')
        db.session.add(log)
        db.session.commit()

        return send_file(filepath, as_attachment=True,
                         download_name=f'ARM_Report_{dataset.name}.pdf')

    except ImportError:
        flash('PDF generation requires reportlab. Install with: pip install reportlab', 'warning')
        return redirect(url_for('reports.index'))
