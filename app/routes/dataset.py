"""
Dataset Management Routes - Upload, View, Delete CSV datasets
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import Dataset, ActivityLog
from app import db
import pandas as pd
import os
from werkzeug.utils import secure_filename

dataset_bp = Blueprint('dataset', __name__, url_prefix='/dataset')


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def validate_csv(filepath):
    """Validate CSV structure - must have Transaction_ID and Items columns"""
    try:
        df = pd.read_csv(filepath)
        required_cols = ['Transaction_ID', 'Items']
        # Case-insensitive check
        df.columns = [col.strip() for col in df.columns]
        has_cols = all(
            any(col.lower() == req.lower() for col in df.columns)
            for req in required_cols
        )
        if not has_cols:
            return False, "CSV must contain 'Transaction_ID' and 'Items' columns"
        if len(df) < 10:
            return False, "Dataset must contain at least 10 transactions"
        return True, df
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"


@dataset_bp.route('/')
@login_required
def index():
    """View all uploaded datasets"""
    datasets = Dataset.query.filter_by(user_id=current_user.id).order_by(
        Dataset.uploaded_at.desc()).all()
    return render_template('dataset/index.html', datasets=datasets)


@dataset_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload a new CSV dataset"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            import time
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Validate CSV
            valid, result = validate_csv(filepath)
            if not valid:
                os.remove(filepath)
                flash(f'Invalid CSV: {result}', 'danger')
                return redirect(request.url)

            df = result
            # Standardize column names
            col_map = {}
            for col in df.columns:
                if col.lower().strip() == 'transaction_id':
                    col_map[col] = 'Transaction_ID'
                elif col.lower().strip() == 'items':
                    col_map[col] = 'Items'
            df.rename(columns=col_map, inplace=True)
            df.to_csv(filepath, index=False)

            # Count unique items
            all_items = set()
            for items_str in df['Items'].dropna():
                items = [i.strip().lower() for i in str(items_str).split(',')]
                all_items.update(items)

            # Save to database
            dataset = Dataset(
                name=request.form.get('name', file.filename),
                filename=filename,
                filepath=filepath,
                total_transactions=len(df),
                total_items=len(all_items),
                user_id=current_user.id
            )
            db.session.add(dataset)

            log = ActivityLog(user_id=current_user.id, action='Upload Dataset',
                              details=f'Uploaded {filename} ({len(df)} transactions)')
            db.session.add(log)
            db.session.commit()

            flash(f'Dataset uploaded successfully! {len(df)} transactions, '
                  f'{len(all_items)} unique items.', 'success')
            return redirect(url_for('dataset.index'))
        else:
            flash('Only CSV files are allowed.', 'danger')

    return render_template('dataset/upload.html')


@dataset_bp.route('/view/<int:dataset_id>')
@login_required
def view(dataset_id):
    """View dataset details"""
    dataset = Dataset.query.get_or_404(dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('dataset.index'))

    df = pd.read_csv(dataset.filepath)
    preview = df.head(20).to_html(classes='table table-striped table-sm', index=False)
    return render_template('dataset/view.html', dataset=dataset, preview=preview,
                           total_rows=len(df))


@dataset_bp.route('/delete/<int:dataset_id>', methods=['POST'])
@login_required
def delete(dataset_id):
    """Delete a dataset"""
    dataset = Dataset.query.get_or_404(dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('dataset.index'))

    # Delete file
    if os.path.exists(dataset.filepath):
        os.remove(dataset.filepath)

    # Delete related mining results
    MiningResult.query.filter_by(dataset_id=dataset.id).delete()

    db.session.delete(dataset)
    log = ActivityLog(user_id=current_user.id, action='Delete Dataset',
                      details=f'Deleted {dataset.name}')
    db.session.add(log)
    db.session.commit()

    flash('Dataset deleted successfully.', 'success')
    return redirect(url_for('dataset.index'))
