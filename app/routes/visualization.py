"""
Visualization Routes - Interactive charts and graphs
"""
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Dataset, MiningResult
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import networkx as nx
import json
import os

visualization_bp = Blueprint('visualization', __name__, url_prefix='/visualization')


@visualization_bp.route('/')
@login_required
def index():
    """Visualization dashboard"""
    datasets = Dataset.query.filter_by(
        user_id=current_user.id, is_preprocessed=True
    ).order_by(Dataset.uploaded_at.desc()).all()
    return render_template('visualization/index.html', datasets=datasets)


@visualization_bp.route('/generate/<int:dataset_id>')
@login_required
def generate(dataset_id):
    """Generate all visualizations for a dataset"""
    dataset = Dataset.query.get_or_404(dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('visualization.index'))

    df = pd.read_csv(dataset.filepath)
    charts_dir = current_app.config['CHARTS_FOLDER']

    # Parse transactions
    transactions = []
    for items_str in df['Items']:
        items = [i.strip() for i in str(items_str).split(',')]
        transactions.append(items)

    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_encoded = pd.DataFrame(te_array, columns=te.columns_)

    # Generate frequent itemsets and rules
    frequent_itemsets = apriori(df_encoded, min_support=0.15, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence",
                              min_threshold=0.4,
                              num_itemsets=len(frequent_itemsets))
    rules = rules.sort_values('lift', ascending=False)

    charts = []

    # Chart 1: Network Graph
    try:
        G = nx.DiGraph()
        for _, row in rules.head(15).iterrows():
            ant = ', '.join(sorted(row['antecedents']))
            con = ', '.join(sorted(row['consequents']))
            G.add_edge(ant, con, weight=row['lift'])

        fig, ax = plt.subplots(figsize=(14, 10))
        pos = nx.spring_layout(G, k=2, seed=42)
        edge_weights = [G[u][v]['weight'] * 1.5 for u, v in G.edges()]
        nx.draw_networkx_nodes(G, pos, node_color='#4FC3F7', node_size=2000,
                               edgecolors='black', linewidths=1.5, ax=ax)
        nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.6,
                               edge_color='#455A64', arrows=True, arrowsize=20, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
        ax.set_title('Association Rules Network Graph', fontsize=14, fontweight='bold')
        ax.axis('off')
        plt.tight_layout()
        path = os.path.join(charts_dir, f'viz_network_{dataset_id}.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        charts.append({'name': 'Association Rules Network Graph', 'path': f'charts/viz_network_{dataset_id}.png',
                       'description': 'Shows relationships between items. Thicker edges indicate stronger associations (higher lift).'})
    except Exception:
        pass

    # Chart 2: Support vs Confidence vs Lift (Bubble Chart)
    if not rules.empty:
        fig, ax = plt.subplots(figsize=(10, 7))
        scatter = ax.scatter(rules['support'], rules['confidence'],
                             s=rules['lift'] * 100, c=rules['lift'],
                             cmap='plasma', alpha=0.6, edgecolors='black')
        plt.colorbar(scatter, ax=ax, label='Lift')
        ax.set_xlabel('Support', fontsize=12, fontweight='bold')
        ax.set_ylabel('Confidence', fontsize=12, fontweight='bold')
        ax.set_title('Rules: Support vs Confidence (Bubble size = Lift)',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        path = os.path.join(charts_dir, f'viz_bubble_{dataset_id}.png')
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        charts.append({'name': 'Support vs Confidence Bubble Chart', 'path': f'charts/viz_bubble_{dataset_id}.png',
                       'description': 'Each bubble represents a rule. Larger bubbles have higher lift values.'})

    # Chart 3: Item Correlation Matrix
    item_freq = df_encoded.sum().sort_values(ascending=False)
    top_items = item_freq.head(10).index.tolist()
    corr_matrix = df_encoded[top_items].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, linewidths=0.5, ax=ax, square=True)
    ax.set_title('Item Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(charts_dir, f'viz_corr_{dataset_id}.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    charts.append({'name': 'Item Correlation Matrix', 'path': f'charts/viz_corr_{dataset_id}.png',
                   'description': 'Shows correlation between items. Positive values (red) indicate items bought together.'})

    # Chart 4: Itemset Size Distribution
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(len)
    size_dist = frequent_itemsets['length'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(size_dist.index, size_dist.values, color='#26A69A', edgecolor='black')
    ax.set_xlabel('Itemset Size', fontsize=12, fontweight='bold')
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title('Frequent Itemset Size Distribution', fontsize=14, fontweight='bold')
    ax.set_xticks(size_dist.index)
    plt.tight_layout()
    path = os.path.join(charts_dir, f'viz_size_{dataset_id}.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    charts.append({'name': 'Itemset Size Distribution', 'path': f'charts/viz_size_{dataset_id}.png',
                   'description': 'Shows how many frequent itemsets exist for each size (1-item, 2-item, etc.).'})

    return render_template('visualization/results.html',
                           dataset=dataset, charts=charts)
