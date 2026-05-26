"""
Exploratory Data Analysis Routes - Generate charts and statistics
"""
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Dataset
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import json

eda_bp = Blueprint('eda', __name__, url_prefix='/eda')


@eda_bp.route('/')
@login_required
def index():
    """Select dataset for EDA"""
    datasets = Dataset.query.filter_by(
        user_id=current_user.id, is_preprocessed=True
    ).order_by(Dataset.uploaded_at.desc()).all()
    return render_template('eda/index.html', datasets=datasets)


@eda_bp.route('/analyze/<int:dataset_id>')
@login_required
def analyze(dataset_id):
    """Perform EDA on selected dataset"""
    dataset = Dataset.query.get_or_404(dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('eda.index'))

    df = pd.read_csv(dataset.filepath)
    charts_dir = current_app.config['CHARTS_FOLDER']

    # Parse items
    all_items = []
    transactions = []
    for items_str in df['Items']:
        items = [i.strip() for i in str(items_str).split(',')]
        all_items.extend(items)
        transactions.append(items)

    # Item frequency
    from collections import Counter
    item_counts = Counter(all_items)
    item_freq = pd.DataFrame(item_counts.items(), columns=['Item', 'Frequency'])
    item_freq = item_freq.sort_values('Frequency', ascending=False).reset_index(drop=True)
    item_freq['Support(%)'] = (item_freq['Frequency'] / len(df) * 100).round(2)

    # Generate charts
    # Chart 1: Top Selling Items Bar Chart
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(item_freq)))
    bars = ax.bar(item_freq['Item'], item_freq['Frequency'], color=colors, edgecolor='black', linewidth=0.5)
    ax.set_xlabel('Items', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title('Item Frequency Analysis - Top Selling Items', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)
    plt.tight_layout()
    chart1_path = os.path.join(charts_dir, f'eda_bar_{dataset_id}.png')
    plt.savefig(chart1_path, dpi=150, bbox_inches='tight')
    plt.close()

    # Chart 2: Pie Chart of Top 8 Items
    fig, ax = plt.subplots(figsize=(8, 8))
    top8 = item_freq.head(8)
    explode = [0.05] * len(top8)
    ax.pie(top8['Frequency'], labels=top8['Item'], autopct='%1.1f%%',
           explode=explode, shadow=True, startangle=90)
    ax.set_title('Distribution of Top 8 Items', fontsize=14, fontweight='bold')
    plt.tight_layout()
    chart2_path = os.path.join(charts_dir, f'eda_pie_{dataset_id}.png')
    plt.savefig(chart2_path, dpi=150, bbox_inches='tight')
    plt.close()

    # Chart 3: Co-occurrence Heatmap
    from mlxtend.preprocessing import TransactionEncoder
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_encoded = pd.DataFrame(te_array, columns=te.columns_)

    top_items_list = item_freq.head(10)['Item'].tolist()
    df_top = df_encoded[top_items_list]
    co_occurrence = df_top.T.dot(df_top)
    np.fill_diagonal(co_occurrence.values, 0)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(co_occurrence, annot=True, fmt='d', cmap='YlOrRd',
                linewidths=0.5, ax=ax, square=True)
    ax.set_title('Item Co-occurrence Heatmap', fontsize=14, fontweight='bold')
    plt.tight_layout()
    chart3_path = os.path.join(charts_dir, f'eda_heatmap_{dataset_id}.png')
    plt.savefig(chart3_path, dpi=150, bbox_inches='tight')
    plt.close()

    # Items per transaction
    items_per_trans = [len(t) for t in transactions]
    stats = {
        'avg_items': round(np.mean(items_per_trans), 2),
        'min_items': min(items_per_trans),
        'max_items': max(items_per_trans),
        'total_transactions': len(df),
        'unique_items': len(item_counts)
    }

    # Chart filenames for template
    charts = {
        'bar': f'charts/eda_bar_{dataset_id}.png',
        'pie': f'charts/eda_pie_{dataset_id}.png',
        'heatmap': f'charts/eda_heatmap_{dataset_id}.png'
    }

    freq_table = item_freq.to_html(classes='table table-striped table-sm', index=False)
    co_occ_table = co_occurrence.to_html(classes='table table-striped table-sm')

    return render_template('eda/results.html',
                           dataset=dataset, stats=stats,
                           charts=charts, freq_table=freq_table,
                           co_occ_table=co_occ_table)
