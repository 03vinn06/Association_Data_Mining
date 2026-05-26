"""
Frequent Itemset Mining Routes - Apriori and FP-Growth algorithms
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import Dataset, MiningResult, ActivityLog
from app import db
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.preprocessing import TransactionEncoder
import json
import os

mining_bp = Blueprint('mining', __name__, url_prefix='/mining')


@mining_bp.route('/')
@login_required
def index():
    """Select dataset and configure mining parameters"""
    datasets = Dataset.query.filter_by(
        user_id=current_user.id, is_preprocessed=True
    ).order_by(Dataset.uploaded_at.desc()).all()
    return render_template('mining/index.html', datasets=datasets)


@mining_bp.route('/run', methods=['POST'])
@login_required
def run():
    """Execute frequent itemset mining"""
    dataset_id = request.form.get('dataset_id', type=int)
    algorithm = request.form.get('algorithm', 'apriori')
    min_support = request.form.get('min_support', 0.20, type=float)
    min_confidence = request.form.get('min_confidence', 0.50, type=float)
    min_lift = request.form.get('min_lift', 1.0, type=float)

    dataset = Dataset.query.get_or_404(dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('mining.index'))

    # Load and prepare data
    df = pd.read_csv(dataset.filepath)
    transactions = []
    for items_str in df['Items']:
        items = [i.strip() for i in str(items_str).split(',')]
        transactions.append(items)

    # Encode transactions
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_encoded = pd.DataFrame(te_array, columns=te.columns_)

    # Run algorithm
    try:
        if algorithm == 'fpgrowth':
            frequent_itemsets = fpgrowth(df_encoded, min_support=min_support, use_colnames=True)
        else:
            frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)

        if frequent_itemsets.empty:
            flash('No frequent itemsets found. Try lowering the minimum support.', 'warning')
            return redirect(url_for('mining.index'))

        frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(len)
        frequent_itemsets = frequent_itemsets.sort_values('support', ascending=False).reset_index(drop=True)

        # Convert to JSON-serializable format
        itemsets_data = []
        for _, row in frequent_itemsets.iterrows():
            itemsets_data.append({
                'itemset': ', '.join(sorted(row['itemsets'])),
                'support': round(row['support'], 4),
                'count': int(row['support'] * len(df_encoded)),
                'length': int(row['length'])
            })

        # Save mining result
        result = MiningResult(
            dataset_id=dataset.id,
            algorithm=algorithm,
            min_support=min_support,
            min_confidence=min_confidence,
            min_lift=min_lift,
            num_frequent_itemsets=len(frequent_itemsets),
            frequent_itemsets_json=json.dumps(itemsets_data)
        )
        db.session.add(result)

        log = ActivityLog(user_id=current_user.id, action='Run Mining',
                          details=f'{algorithm.upper()} on {dataset.name}: '
                                  f'{len(frequent_itemsets)} itemsets found')
        db.session.add(log)
        db.session.commit()

        # Generate chart
        charts_dir = current_app.config['CHARTS_FOLDER']
        fig, ax = plt.subplots(figsize=(12, 6))
        top_itemsets = frequent_itemsets.head(15)
        labels = [', '.join(sorted(x)) for x in top_itemsets['itemsets']]
        ax.barh(range(len(top_itemsets)), top_itemsets['support'],
                color='coral', edgecolor='black', linewidth=0.5)
        ax.set_yticks(range(len(top_itemsets)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel('Support', fontsize=12, fontweight='bold')
        ax.set_title(f'Top Frequent Itemsets ({algorithm.upper()}, min_support={min_support})',
                     fontsize=14, fontweight='bold')
        ax.axvline(x=min_support, color='red', linestyle='--', label=f'Min Support = {min_support}')
        ax.legend()
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, f'mining_{dataset_id}.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        # Statistics
        stats = {
            'algorithm': algorithm.upper(),
            'min_support': min_support,
            'total_itemsets': len(frequent_itemsets),
            'one_item': len(frequent_itemsets[frequent_itemsets['length'] == 1]),
            'two_item': len(frequent_itemsets[frequent_itemsets['length'] == 2]),
            'three_plus': len(frequent_itemsets[frequent_itemsets['length'] >= 3]),
            'min_threshold_count': int(min_support * len(df_encoded))
        }

        return render_template('mining/results.html',
                               dataset=dataset, itemsets=itemsets_data,
                               stats=stats, result_id=result.id,
                               chart=f'charts/mining_{dataset_id}.png')

    except Exception as e:
        flash(f'Error during mining: {str(e)}', 'danger')
        return redirect(url_for('mining.index'))
