"""
Dashboard Routes - Main system dashboard with analytics overview
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Dataset, MiningResult
from app import db
import json

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard with system overview"""
    # Get statistics
    total_datasets = Dataset.query.filter_by(user_id=current_user.id).count()
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()

    total_transactions = sum(d.total_transactions for d in datasets)
    total_items = max((d.total_items for d in datasets), default=0)

    # Get latest mining results
    latest_result = MiningResult.query.join(Dataset).filter(
        Dataset.user_id == current_user.id
    ).order_by(MiningResult.created_at.desc()).first()

    num_frequent_itemsets = 0
    num_rules = 0
    strongest_rule = None
    top_items = []

    if latest_result:
        num_frequent_itemsets = latest_result.num_frequent_itemsets
        num_rules = latest_result.num_rules

        if latest_result.rules_json:
            rules = json.loads(latest_result.rules_json)
            if rules:
                strongest_rule = max(rules, key=lambda x: x.get('lift', 0))

    return render_template('dashboard/index.html',
                           total_datasets=total_datasets,
                           total_transactions=total_transactions,
                           total_items=total_items,
                           num_frequent_itemsets=num_frequent_itemsets,
                           num_rules=num_rules,
                           strongest_rule=strongest_rule,
                           datasets=datasets)
