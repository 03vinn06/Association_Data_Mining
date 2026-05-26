"""
Business Recommendation Engine Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Dataset, MiningResult
import json

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/recommendations')


@recommendations_bp.route('/')
@login_required
def index():
    """Select dataset for recommendations"""
    results = MiningResult.query.join(Dataset).filter(
        Dataset.user_id == current_user.id,
        MiningResult.rules_json.isnot(None)
    ).order_by(MiningResult.created_at.desc()).all()
    return render_template('recommendations/index.html', results=results)


@recommendations_bp.route('/generate/<int:result_id>')
@login_required
def generate(result_id):
    """Generate business recommendations from mining results"""
    result = MiningResult.query.get_or_404(result_id)
    dataset = Dataset.query.get(result.dataset_id)
    if dataset.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('recommendations.index'))

    if not result.rules_json:
        flash('No rules available. Run association rule generation first.', 'warning')
        return redirect(url_for('recommendations.index'))

    rules = json.loads(result.rules_json)

    # Generate recommendations
    recommendations = generate_recommendations(rules)

    return render_template('recommendations/results.html',
                           dataset=dataset, result=result,
                           recommendations=recommendations, rules=rules[:10])


def generate_recommendations(rules):
    """AI-style recommendation engine"""
    recommendations = {
        'bundles': [],
        'cross_selling': [],
        'store_layout': [],
        'promotions': [],
        'high_demand': [],
        'marketing': []
    }

    if not rules:
        return recommendations

    # Sort by different metrics
    by_lift = sorted(rules, key=lambda x: x['lift'], reverse=True)
    by_confidence = sorted(rules, key=lambda x: x['confidence'], reverse=True)
    by_support = sorted(rules, key=lambda x: x['support'], reverse=True)

    # Product Bundle Recommendations (top lift rules)
    for rule in by_lift[:5]:
        bundle_items = rule['antecedents'] + ' + ' + rule['consequents']
        score = round(rule['lift'] * rule['confidence'] * 100, 1)
        recommendations['bundles'].append({
            'items': bundle_items,
            'reason': f"Lift of {rule['lift']:.2f} indicates these items are "
                      f"{((rule['lift']-1)*100):.0f}% more likely to be bought together.",
            'confidence': f"{rule['confidence']*100:.1f}%",
            'score': score
        })

    # Cross-selling Recommendations (high confidence)
    for rule in by_confidence[:5]:
        recommendations['cross_selling'].append({
            'trigger': rule['antecedents'],
            'suggest': rule['consequents'],
            'reason': f"{rule['confidence']*100:.1f}% of customers who buy "
                      f"{rule['antecedents']} also buy {rule['consequents']}.",
            'confidence': f"{rule['confidence']*100:.1f}%"
        })

    # Store Layout Suggestions
    seen_pairs = set()
    for rule in by_lift[:8]:
        pair = tuple(sorted([rule['antecedents'], rule['consequents']]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            recommendations['store_layout'].append({
                'items': f"{rule['antecedents']} and {rule['consequents']}",
                'suggestion': f"Place {rule['antecedents']} near {rule['consequents']} "
                              f"(Lift: {rule['lift']:.2f})",
                'reason': 'Strong positive correlation indicates customers look for these together.'
            })

    # Promotional Combinations
    for rule in by_support[:5]:
        recommendations['promotions'].append({
            'promotion': f"Buy {rule['antecedents']}, Get {rule['consequents']} at discount",
            'expected_reach': f"{rule['support']*100:.1f}% of customers",
            'success_rate': f"{rule['confidence']*100:.1f}% conversion expected"
        })

    # High Demand Products (from antecedents with high support)
    item_mentions = {}
    for rule in rules:
        for item in rule['antecedents'].split(', '):
            item = item.strip()
            if item not in item_mentions:
                item_mentions[item] = {'count': 0, 'total_support': 0}
            item_mentions[item]['count'] += 1
            item_mentions[item]['total_support'] += rule['support']

    sorted_items = sorted(item_mentions.items(),
                          key=lambda x: x[1]['total_support'], reverse=True)
    for item, data in sorted_items[:5]:
        recommendations['high_demand'].append({
            'item': item,
            'appears_in_rules': data['count'],
            'insight': f"Appears in {data['count']} association rules. "
                       f"Key connector product - ensure consistent stock."
        })

    # Marketing Insights
    recommendations['marketing'] = [
        {
            'strategy': 'Bundle Pricing',
            'description': 'Offer discounted bundles for top associated item pairs.',
            'based_on': f"Top rule: {by_lift[0]['antecedents']} → {by_lift[0]['consequents']}" if by_lift else ''
        },
        {
            'strategy': 'Cross-sell at Checkout',
            'description': 'Suggest complementary items at point of sale based on cart contents.',
            'based_on': f"High confidence rules (>{by_confidence[0]['confidence']*100:.0f}%)" if by_confidence else ''
        },
        {
            'strategy': 'Loyalty Rewards',
            'description': 'Offer bonus points when customers purchase frequently associated items together.',
            'based_on': 'High-support itemsets indicate popular combinations.'
        },
        {
            'strategy': 'Targeted Email Campaigns',
            'description': 'Send personalized recommendations based on purchase history patterns.',
            'based_on': 'Association rules reveal customer buying preferences.'
        }
    ]

    return recommendations
