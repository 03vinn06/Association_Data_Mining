"""
Data Preprocessing Routes - Clean and prepare datasets for mining
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Dataset, ActivityLog
from app import db
import pandas as pd

preprocessing_bp = Blueprint('preprocessing', __name__, url_prefix='/preprocessing')


@preprocessing_bp.route('/')
@login_required
def index():
    """Select dataset for preprocessing"""
    datasets = Dataset.query.filter_by(user_id=current_user.id).order_by(
        Dataset.uploaded_at.desc()).all()
    return render_template('preprocessing/index.html', datasets=datasets)


@preprocessing_bp.route('/process/<int:dataset_id>')
@login_required
def process(dataset_id):
    """Preprocess the selected dataset"""
    dataset = Dataset.query.get_or_404(dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('preprocessing.index'))

    df = pd.read_csv(dataset.filepath)
    original_count = len(df)
    steps = []

    # Step 1: Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    removed_dupes = before - len(df)
    steps.append({
        'step': 'Remove Duplicate Transactions',
        'description': 'Identified and removed exact duplicate rows to ensure data integrity.',
        'before': before,
        'after': len(df),
        'removed': removed_dupes
    })

    # Step 2: Remove missing values
    before = len(df)
    df = df.dropna(subset=['Transaction_ID', 'Items'])
    removed_missing = before - len(df)
    steps.append({
        'step': 'Remove Incomplete Records',
        'description': 'Removed transactions with missing Transaction_ID or Items values.',
        'before': before,
        'after': len(df),
        'removed': removed_missing
    })

    # Step 3: Remove empty items
    before = len(df)
    df = df[df['Items'].str.strip() != '']
    removed_empty = before - len(df)
    steps.append({
        'step': 'Remove Empty Transactions',
        'description': 'Removed transactions where the Items field is empty.',
        'before': before,
        'after': len(df),
        'removed': removed_empty
    })

    # Step 4: Standardize item names
    def standardize(items_str):
        items = [item.strip().title() for item in str(items_str).split(',')]
        items = [item for item in items if item]  # Remove empty strings
        return ', '.join(items)

    df['Items'] = df['Items'].apply(standardize)
    steps.append({
        'step': 'Standardize Item Names',
        'description': 'Applied Title Case formatting, removed extra spaces, '
                       'and ensured consistent naming across all items.',
        'before': len(df),
        'after': len(df),
        'removed': 0
    })

    # Step 5: Reset Transaction IDs
    df['Transaction_ID'] = [f'T{str(i+1).zfill(3)}' for i in range(len(df))]
    steps.append({
        'step': 'Reset Transaction IDs',
        'description': 'Reassigned sequential Transaction IDs after cleaning.',
        'before': len(df),
        'after': len(df),
        'removed': 0
    })

    # Save cleaned dataset
    df.to_csv(dataset.filepath, index=False)

    # Update dataset record
    all_items = set()
    for items_str in df['Items']:
        items = [i.strip() for i in str(items_str).split(',')]
        all_items.update(items)

    dataset.total_transactions = len(df)
    dataset.total_items = len(all_items)
    dataset.is_preprocessed = True

    log = ActivityLog(user_id=current_user.id, action='Preprocess Dataset',
                      details=f'Preprocessed {dataset.name}: {original_count} → {len(df)} records')
    db.session.add(log)
    db.session.commit()

    summary = {
        'original_count': original_count,
        'cleaned_count': len(df),
        'total_removed': original_count - len(df),
        'unique_items': len(all_items)
    }

    preview = df.head(15).to_html(classes='table table-striped table-sm', index=False)

    return render_template('preprocessing/results.html',
                           dataset=dataset, steps=steps,
                           summary=summary, preview=preview)
