"""
Association Rule Generation Routes
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
import seaborn as sns
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import json
import os

rules_bp = Blueprint('rules', __name__, url_prefix='/rules')


@rules_bp.route('/')
@login_required
def index():
    """Select dataset for rule generation"""
    datasets = Dataset.query.filter_by(
        user_id=current_user.id, is_preprocessed=True
    ).order_by(Dataset.uploaded_at.desc()).all()
    results = MiningResult.query.join(Dataset).filter(
        Dataset.user_id == current_user.id
    ).order_by(MiningResult.created_at.desc()).all()
    return render_template('rules/index.html', datasets=datasets, results=results)


@rules_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    """Generate association rules"""
    dataset_id = request.form.get('dataset_id', type=int)
    algorithm = request.form.get('algorithm', 'apriori')
    min_support = request.form.get('min_support', 0.20, type=float)
    min_confidence = request.form.get('min_confidence', 0.50, type=float)
    min_lift = request.form.get('min_lift', 1.0, type=float)

    dataset = Dataset.query.get_or_404(dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('rules.index'))

    # Load and prepare data
    df = pd.read_csv(dataset.filepath)
    transactions = []
    for items_str in df['Items']:
        items = [i.strip() for i in str(items_str).split(',')]
        transactions.append(items)

    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_encoded = pd.DataFrame(te_array, columns=te.columns_)

    try:
        # Generate frequent itemsets
        if algorithm == 'fpgrowth':
            frequent_itemsets = fpgrowth(df_encoded, min_support=min_support, use_colnames=True)
        else:
            frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)

        if frequent_itemsets.empty:
            flash('No frequent itemsets found. Lower the support threshold.', 'warning')
            return redirect(url_for('rules.index'))

        # Generate rules
        rules = association_rules(frequent_itemsets, metric="confidence",
                                  min_threshold=min_confidence,
                                  num_itemsets=len(frequent_itemsets))

        if rules.empty:
            flash('No rules generated. Try lowering confidence threshold.', 'warning')
            return redirect(url_for('rules.index'))

        # Filter by lift
        rules = rules[rules['lift'] >= min_lift]
        rules = rules.sort_values('lift', ascending=False).reset_index(drop=True)

        # Convert to JSON
        rules_data = []
        for _, row in rules.iterrows():
            rules_data.append({
                'antecedents': ', '.join(sorted(row['antecedents'])),
                'consequents': ', '.join(sorted(row['consequents'])),
                'support': round(row['support'], 4),
                'confidence': round(row['confidence'], 4),
                'lift': round(row['lift'], 4)
            })

        # Update or create mining result
        result = MiningResult.query.filter_by(
            dataset_id=dataset.id, algorithm=algorithm
        ).first()

        if not result:
            result = MiningResult(
                dataset_id=dataset.id,
                algorithm=algorithm,
                min_support=min_support,
                min_confidence=min_confidence,
                min_lift=min_lift
            )
            db.session.add(result)

        result.num_frequent_itemsets = len(frequent_itemsets)
        result.num_rules = len(rules)
        result.rules_json = json.dumps(rules_data)
        result.min_confidence = min_confidence
        result.min_lift = min_lift

        log = ActivityLog(user_id=current_user.id, action='Generate Rules',
                          details=f'{len(rules)} rules from {dataset.name}')
        db.session.add(log)
        db.session.commit()

        # Generate charts
        charts_dir = current_app.config['CHARTS_FOLDER']

        # Chart 1: Support vs Confidence
        fig, ax = plt.subplots(figsize=(10, 7))
        scatter = ax.scatter(rules['support'], rules['confidence'],
                             c=rules['lift'], cmap='RdYlGn', s=100,
                             alpha=0.7, edgecolors='black', linewidth=0.5)
        plt.colorbar(scatter, ax=ax, label='Lift')
        ax.set_xlabel('Support', fontsize=12, fontweight='bold')
        ax.set_ylabel('Confidence', fontsize=12, fontweight='bold')
        ax.set_title('Association Rules: Support vs Confidence', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, f'rules_scatter_{dataset_id}.png'), dpi=150)
        plt.close()

        # Chart 2: Top Rules by Lift
        fig, ax = plt.subplots(figsize=(12, 7))
        top_rules = rules.head(10)
        rule_labels = [f"{', '.join(sorted(r['antecedents']))} → {', '.join(sorted(r['consequents']))}"
                       for _, r in top_rules.iterrows()]
        ax.barh(range(len(top_rules)), top_rules['lift'],
                color=plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(top_rules))),
                edgecolor='black', linewidth=0.5)
        ax.set_yticks(range(len(top_rules)))
        ax.set_yticklabels(rule_labels, fontsize=9)
        ax.set_xlabel('Lift', fontsize=12, fontweight='bold')
        ax.set_title('Top 10 Association Rules by Lift', fontsize=14, fontweight='bold')
        ax.axvline(x=1, color='red', linestyle='--', label='Lift = 1')
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, f'rules_lift_{dataset_id}.png'), dpi=150)
        plt.close()

        charts = {
            'scatter': f'charts/rules_scatter_{dataset_id}.png',
            'lift': f'charts/rules_lift_{dataset_id}.png'
        }

        stats = {
            'algorithm': algorithm.upper(),
            'total_rules': len(rules),
            'min_support': min_support,
            'min_confidence': min_confidence,
            'min_lift': min_lift,
            'avg_confidence': round(rules['confidence'].mean(), 4),
            'avg_lift': round(rules['lift'].mean(), 4),
            'max_lift': round(rules['lift'].max(), 4)
        }

        return render_template('rules/results.html',
                               dataset=dataset, rules=rules_data,
                               stats=stats, charts=charts)

    except Exception as e:
        flash(f'Error generating rules: {str(e)}', 'danger')
        return redirect(url_for('rules.index'))
