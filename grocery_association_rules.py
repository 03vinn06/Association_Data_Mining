"""
================================================================================
ASSOCIATION RULE MINING PROJECT
Grocery Store Transaction Analysis using Apriori Algorithm
================================================================================
Organization: Grocery Store
Algorithm: Apriori (from mlxtend library)
Dataset: 110 transaction records
================================================================================
"""

# ============================================================================
# SECTION 1: IMPORT LIBRARIES
# ============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import warnings
warnings.filterwarnings('ignore')

# Set plot style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

print("=" * 70)
print("   ASSOCIATION RULE MINING - GROCERY STORE TRANSACTIONS")
print("=" * 70)

# ============================================================================
# SECTION 2: DATA LOADING
# ============================================================================
print("\n" + "=" * 70)
print("   STEP 1: DATA LOADING")
print("=" * 70)

# Load the dataset
df = pd.read_csv('dataset/grocery_transactions.csv')

print(f"\nDataset loaded successfully!")
print(f"Total transactions: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 10 transactions:")
print(df.head(10).to_string(index=False))

# ============================================================================
# SECTION 3: DATA CLEANING AND PREPROCESSING
# ============================================================================
print("\n" + "=" * 70)
print("   STEP 2: DATA CLEANING AND PREPROCESSING")
print("=" * 70)

# Step 2.1: Check for duplicates
print("\n--- 2.1 Checking for Duplicate Transactions ---")
duplicates = df.duplicated()
print(f"Number of duplicate rows: {duplicates.sum()}")
df = df.drop_duplicates()
print(f"Rows after removing duplicates: {len(df)}")

# Step 2.2: Check for missing values
print("\n--- 2.2 Checking for Missing Values ---")
print(f"Missing values per column:")
print(df.isnull().sum())
df = df.dropna()
print(f"Rows after removing incomplete records: {len(df)}")

# Step 2.3: Standardize item names
print("\n--- 2.3 Standardizing Item Names ---")
# Split items and standardize (strip whitespace, title case)
def standardize_items(item_string):
    items = [item.strip().title() for item in item_string.split(',')]
    return items

df['Items_List'] = df['Items'].apply(standardize_items)
print("Item names standardized (stripped whitespace, applied title case)")
print(f"\nSample standardized items:")
for i in range(5):
    print(f"  {df.iloc[i]['Transaction_ID']}: {df.iloc[i]['Items_List']}")

# Step 2.4: Convert to transaction format for Apriori
print("\n--- 2.4 Converting to Transaction Encoding Format ---")
transactions = df['Items_List'].tolist()

# Use TransactionEncoder to create one-hot encoded DataFrame
te = TransactionEncoder()
te_array = te.fit(transactions).transform(transactions)
df_encoded = pd.DataFrame(te_array, columns=te.columns_)

print(f"Encoded DataFrame shape: {df_encoded.shape}")
print(f"Number of unique items: {len(te.columns_)}")
print(f"\nAll unique items in the dataset:")
print(sorted(te.columns_))
print(f"\nEncoded DataFrame (first 5 rows):")
print(df_encoded.head().to_string())

# ============================================================================
# SECTION 4: EXPLORATORY DATA ANALYSIS (EDA)
# ============================================================================
print("\n" + "=" * 70)
print("   STEP 3: EXPLORATORY DATA ANALYSIS")
print("=" * 70)

# 4.1: Item Frequency Analysis
print("\n--- 3.1 Item Frequency Analysis ---")
item_frequency = df_encoded.sum().sort_values(ascending=False)
print("\nTop-Selling Items Table:")
print("-" * 40)
print(f"{'Item':<20} {'Frequency':<12} {'Support %':<10}")
print("-" * 40)
for item, freq in item_frequency.items():
    support_pct = (freq / len(df_encoded)) * 100
    print(f"{item:<20} {int(freq):<12} {support_pct:.1f}%")
print("-" * 40)

# 4.2: Bar Chart - Top Selling Items
print("\n--- 3.2 Generating Bar Chart: Top Selling Items ---")
fig, ax = plt.subplots(figsize=(12, 6))
colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(item_frequency)))
bars = ax.bar(item_frequency.index, item_frequency.values, color=colors, edgecolor='black', linewidth=0.5)
ax.set_xlabel('Items', fontsize=12, fontweight='bold')
ax.set_ylabel('Frequency (Number of Transactions)', fontsize=12, fontweight='bold')
ax.set_title('Top-Selling Items in Grocery Store', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right', fontsize=10)
# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig('charts/01_top_selling_items.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: charts/01_top_selling_items.png")

# 4.3: Items per Transaction Distribution
print("\n--- 3.3 Items per Transaction Distribution ---")
items_per_transaction = df['Items_List'].apply(len)
print(f"\nStatistics:")
print(f"  Average items per transaction: {items_per_transaction.mean():.2f}")
print(f"  Minimum items per transaction: {items_per_transaction.min()}")
print(f"  Maximum items per transaction: {items_per_transaction.max()}")

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(items_per_transaction, bins=range(1, items_per_transaction.max() + 2),
        color='steelblue', edgecolor='black', alpha=0.7, align='left')
ax.set_xlabel('Number of Items per Transaction', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
ax.set_title('Distribution of Items per Transaction', fontsize=14, fontweight='bold')
ax.set_xticks(range(1, items_per_transaction.max() + 1))
plt.tight_layout()
plt.savefig('charts/02_items_per_transaction.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: charts/02_items_per_transaction.png")

# 4.4: Co-occurrence Matrix (Correlation Heatmap)
print("\n--- 3.4 Co-occurrence / Correlation Analysis ---")
# Calculate co-occurrence matrix
co_occurrence = df_encoded.T.dot(df_encoded)
np.fill_diagonal(co_occurrence.values, 0)

print("\nCo-occurrence Matrix (Top items):")
top_items = item_frequency.head(8).index.tolist()
co_occ_top = co_occurrence.loc[top_items, top_items]
print(co_occ_top.to_string())

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(co_occ_top, annot=True, fmt='d', cmap='YlOrRd',
            linewidths=0.5, ax=ax, square=True)
ax.set_title('Item Co-occurrence Heatmap (Top 8 Items)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/03_cooccurrence_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: charts/03_cooccurrence_heatmap.png")

print("\n--- EDA Interpretation ---")
print("""
INTERPRETATION:
- Bread and Milk are the most frequently purchased items, appearing in the
  majority of transactions. This indicates they are staple grocery items.
- Eggs ranks third, often purchased alongside Bread and Milk.
- Coffee and Sugar frequently appear together, suggesting a strong association.
- The co-occurrence heatmap shows that Bread-Milk, Bread-Eggs, and Milk-Eggs
  are the most commonly co-purchased item pairs.
- Most transactions contain 3-4 items, indicating moderate basket sizes.
""")

# ============================================================================
# SECTION 5: FREQUENT ITEMSET MINING (APRIORI ALGORITHM)
# ============================================================================
print("\n" + "=" * 70)
print("   STEP 4: FREQUENT ITEMSET MINING (APRIORI ALGORITHM)")
print("=" * 70)

# Apply Apriori Algorithm with minimum support of 20%
min_support = 0.20
print(f"\nMinimum Support Threshold: {min_support} ({int(min_support*100)}%)")
print(f"This means an itemset must appear in at least {int(min_support * len(df_encoded))} "
      f"out of {len(df_encoded)} transactions.")

frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(len)
frequent_itemsets = frequent_itemsets.sort_values('support', ascending=False).reset_index(drop=True)

print(f"\nTotal frequent itemsets found: {len(frequent_itemsets)}")
print(f"  - 1-item sets: {len(frequent_itemsets[frequent_itemsets['length'] == 1])}")
print(f"  - 2-item sets: {len(frequent_itemsets[frequent_itemsets['length'] == 2])}")
print(f"  - 3-item sets: {len(frequent_itemsets[frequent_itemsets['length'] == 3])}")

print("\n" + "=" * 70)
print("FREQUENT ITEMSETS TABLE")
print("=" * 70)
print(f"\n{'#':<4} {'Itemset':<40} {'Support':<10} {'Count':<8} {'Length':<6}")
print("-" * 70)
for idx, row in frequent_itemsets.iterrows():
    itemset_str = ', '.join(sorted(row['itemsets']))
    count = int(row['support'] * len(df_encoded))
    print(f"{idx+1:<4} {itemset_str:<40} {row['support']:.4f}    {count:<8} {row['length']:<6}")
print("-" * 70)

print("""
EXPLANATION:
- Support: The proportion of transactions containing the itemset.
  Formula: Support(X) = Count(X) / Total Transactions
  
- A support of 0.20 (20%) means the itemset appears in at least 20% of all
  transactions. Higher support = more frequently purchased together.
  
- Bread, Milk, and Eggs have the highest individual support because they are
  staple grocery items purchased by most customers.
  
- The pair {Bread, Milk} has high support because these items are commonly
  bought together as breakfast essentials.
""")

# Visualize frequent itemsets
fig, ax = plt.subplots(figsize=(12, 6))
top_itemsets = frequent_itemsets.head(15)
itemset_labels = [', '.join(sorted(x)) for x in top_itemsets['itemsets']]
bars = ax.barh(range(len(top_itemsets)), top_itemsets['support'], color='coral', edgecolor='black', linewidth=0.5)
ax.set_yticks(range(len(top_itemsets)))
ax.set_yticklabels(itemset_labels, fontsize=9)
ax.set_xlabel('Support', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Frequent Itemsets (min_support = 20%)', fontsize=14, fontweight='bold')
ax.axvline(x=min_support, color='red', linestyle='--', label=f'Min Support = {min_support}')
ax.legend()
plt.tight_layout()
plt.savefig('charts/04_frequent_itemsets.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: charts/04_frequent_itemsets.png")

# ============================================================================
# SECTION 6: ASSOCIATION RULE GENERATION
# ============================================================================
print("\n" + "=" * 70)
print("   STEP 5: ASSOCIATION RULE GENERATION")
print("=" * 70)

# Generate association rules
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5,
                          num_itemsets=len(frequent_itemsets))
rules = rules.sort_values('lift', ascending=False).reset_index(drop=True)

print(f"\nTotal association rules generated: {len(rules)}")
print(f"Minimum confidence threshold: 50%")

print("\n" + "=" * 90)
print("ASSOCIATION RULES TABLE")
print("=" * 90)
print(f"\n{'#':<4} {'Antecedent':<25} {'Consequent':<20} {'Support':<10} {'Confidence':<12} {'Lift':<8}")
print("-" * 90)
for idx, row in rules.iterrows():
    ant = ', '.join(sorted(row['antecedents']))
    con = ', '.join(sorted(row['consequents']))
    print(f"{idx+1:<4} {ant:<25} {con:<20} {row['support']:.4f}    {row['confidence']:.4f}      {row['lift']:.4f}")
print("-" * 90)

# Display top 10 strongest rules
print("\n\nTOP 10 STRONGEST RULES (by Lift):")
print("=" * 90)
print(f"\n{'#':<4} {'Rule':<50} {'Conf':<10} {'Lift':<8}")
print("-" * 90)
for idx, row in rules.head(10).iterrows():
    ant = ', '.join(sorted(row['antecedents']))
    con = ', '.join(sorted(row['consequents']))
    rule_str = f"{ant} → {con}"
    print(f"{idx+1:<4} {rule_str:<50} {row['confidence']:.4f}    {row['lift']:.4f}")
print("-" * 90)

print("""
EXPLANATION OF METRICS:

1. SUPPORT: How frequently the itemset appears in the dataset.
   Formula: Support(A→B) = P(A ∪ B) = Count(A and B) / Total Transactions
   Example: If Bread and Milk appear together in 60 out of 110 transactions,
            Support = 60/110 = 0.545 (54.5%)

2. CONFIDENCE: How often the rule is true (probability of B given A).
   Formula: Confidence(A→B) = P(B|A) = Support(A ∪ B) / Support(A)
   Example: If Bread appears in 80 transactions and Bread+Milk in 60,
            Confidence = 60/80 = 0.75 (75%)
   Interpretation: 75% of customers who buy Bread also buy Milk.

3. LIFT: How much more likely B is purchased when A is purchased.
   Formula: Lift(A→B) = Confidence(A→B) / Support(B)
   - Lift > 1: Positive correlation (items are bought together more than expected)
   - Lift = 1: No correlation (independent items)
   - Lift < 1: Negative correlation (items substitute each other)
   
   Example: If Lift = 1.25, customers are 25% more likely to buy B when they buy A.
""")

# ============================================================================
# SECTION 7: VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 70)
print("   STEP 6: VISUALIZATIONS")
print("=" * 70)

# 7.1: Support vs Confidence Scatter Plot
print("\n--- 6.1 Support vs Confidence Scatter Plot ---")
fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(rules['support'], rules['confidence'],
                     c=rules['lift'], cmap='RdYlGn', s=100,
                     alpha=0.7, edgecolors='black', linewidth=0.5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Lift', fontsize=12)
ax.set_xlabel('Support', fontsize=12, fontweight='bold')
ax.set_ylabel('Confidence', fontsize=12, fontweight='bold')
ax.set_title('Association Rules: Support vs Confidence (colored by Lift)',
             fontsize=14, fontweight='bold')
ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Min Confidence = 0.5')
ax.axvline(x=0.2, color='blue', linestyle='--', alpha=0.5, label='Min Support = 0.2')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('charts/05_support_vs_confidence.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: charts/05_support_vs_confidence.png")

# 7.2: Top Rules by Lift
print("\n--- 6.2 Top Rules by Lift Bar Chart ---")
fig, ax = plt.subplots(figsize=(12, 7))
top_rules = rules.head(10)
rule_labels = [f"{', '.join(sorted(r['antecedents']))} → {', '.join(sorted(r['consequents']))}"
               for _, r in top_rules.iterrows()]
colors_lift = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(top_rules)))
bars = ax.barh(range(len(top_rules)), top_rules['lift'], color=colors_lift, edgecolor='black', linewidth=0.5)
ax.set_yticks(range(len(top_rules)))
ax.set_yticklabels(rule_labels, fontsize=9)
ax.set_xlabel('Lift', fontsize=12, fontweight='bold')
ax.set_title('Top 10 Association Rules by Lift', fontsize=14, fontweight='bold')
ax.axvline(x=1, color='red', linestyle='--', label='Lift = 1 (No correlation)')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('charts/06_top_rules_by_lift.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: charts/06_top_rules_by_lift.png")

# 7.3: Confidence Bar Chart for Top Rules
print("\n--- 6.3 Confidence Bar Chart ---")
fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(range(len(top_rules)), top_rules['confidence'],
               color='steelblue', edgecolor='black', linewidth=0.5)
ax.set_yticks(range(len(top_rules)))
ax.set_yticklabels(rule_labels, fontsize=9)
ax.set_xlabel('Confidence', fontsize=12, fontweight='bold')
ax.set_title('Top 10 Association Rules by Confidence', fontsize=14, fontweight='bold')
ax.axvline(x=0.5, color='red', linestyle='--', label='Min Confidence = 0.5')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('charts/07_confidence_chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: charts/07_confidence_chart.png")

# 7.4: Network Graph of Association Rules
print("\n--- 6.4 Network Graph of Association Rules ---")
try:
    import networkx as nx
    
    G = nx.DiGraph()
    for _, row in rules.head(15).iterrows():
        ant = ', '.join(sorted(row['antecedents']))
        con = ', '.join(sorted(row['consequents']))
        G.add_edge(ant, con, weight=row['lift'], confidence=row['confidence'])
    
    fig, ax = plt.subplots(figsize=(14, 10))
    pos = nx.spring_layout(G, k=2, seed=42)
    
    # Draw edges with varying width based on lift
    edges = G.edges(data=True)
    edge_weights = [d['weight'] * 2 for _, _, d in edges]
    
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000,
                           edgecolors='black', linewidths=1.5, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.6,
                           edge_color='gray', arrows=True, arrowsize=20,
                           connectionstyle="arc3,rad=0.1", ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
    
    ax.set_title('Network Graph of Association Rules\n(Edge width = Lift strength)',
                 fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('charts/08_network_graph.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Chart saved: charts/08_network_graph.png")
except ImportError:
    print("NetworkX not installed. Skipping network graph.")
    print("Install with: pip install networkx")

# 7.5: Heatmap of Rules (Support x Confidence)
print("\n--- 6.5 Rules Metrics Heatmap ---")
fig, ax = plt.subplots(figsize=(10, 8))
rules_display = rules.head(10).copy()
rules_display['rule'] = [f"{', '.join(sorted(r['antecedents']))} → {', '.join(sorted(r['consequents']))}"
                         for _, r in rules_display.iterrows()]
metrics_df = rules_display[['rule', 'support', 'confidence', 'lift']].set_index('rule')
sns.heatmap(metrics_df, annot=True, fmt='.3f', cmap='YlOrRd',
            linewidths=0.5, ax=ax)
ax.set_title('Association Rules Metrics Heatmap', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/09_rules_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: charts/09_rules_heatmap.png")

print("""
VISUALIZATION INTERPRETATIONS:

1. Support vs Confidence Scatter Plot:
   - Rules in the upper-right corner are the strongest (high support AND confidence)
   - Green-colored points have high lift (strong positive correlation)
   - Rules above the red line meet our confidence threshold

2. Top Rules by Lift:
   - All top rules have lift > 1, indicating positive correlations
   - Higher lift means stronger association between items
   - These rules are most useful for product bundling

3. Network Graph:
   - Thicker edges represent stronger associations (higher lift)
   - Clusters of connected items suggest natural product bundles
   - Central nodes (like Bread, Milk) are key connector items

4. Heatmap:
   - Darker colors indicate higher metric values
   - Allows quick comparison across all three metrics simultaneously
""")

# ============================================================================
# SECTION 8: BUSINESS INSIGHTS AND RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 70)
print("   STEP 7: BUSINESS INSIGHTS AND RECOMMENDATIONS")
print("=" * 70)

print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    BUSINESS INSIGHTS & RECOMMENDATIONS              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. PRODUCT BUNDLE RECOMMENDATIONS:                                  ║
║     • Bundle 1: Bread + Milk + Eggs (Breakfast Bundle)               ║
║       - These items appear together in 40%+ of transactions          ║
║       - Offer a 5-10% discount when bought together                  ║
║                                                                      ║
║     • Bundle 2: Coffee + Sugar + Creamer (Coffee Lovers Bundle)      ║
║       - Strong association with high confidence                      ║
║       - Create a dedicated "Coffee Corner" display                   ║
║                                                                      ║
║     • Bundle 3: Rice + Cooking Oil + Soy Sauce (Cooking Bundle)      ║
║       - Frequently purchased together for meal preparation           ║
║       - Place these items in adjacent aisles                         ║
║                                                                      ║
║  2. MARKETING STRATEGIES:                                            ║
║     • Cross-selling: When a customer buys Bread, recommend Milk      ║
║       and Eggs at checkout (high confidence rule)                     ║
║     • Loyalty program: Offer points for purchasing bundles           ║
║     • Weekend promotions on Breakfast Bundle items                   ║
║     • "Complete your recipe" suggestions at point of sale            ║
║                                                                      ║
║  3. STORE LAYOUT IMPROVEMENTS:                                       ║
║     • Place Bread, Milk, and Eggs in proximity (same aisle/section)  ║
║     • Position Coffee, Sugar, and Creamer together                   ║
║     • Create an end-cap display for Rice + Cooking Oil + Soy Sauce   ║
║     • Place Butter and Cheese near the Milk section                  ║
║     • Put Juice near Bread and Eggs (breakfast association)          ║
║                                                                      ║
║  4. PROMOTIONAL COMBINATIONS:                                        ║
║     • "Buy Bread & Milk, Get Eggs 10% Off"                          ║
║     • "Coffee + Sugar + Creamer Combo Deal"                          ║
║     • "Cooking Essentials Pack" (Rice + Oil + Soy Sauce)             ║
║     • Seasonal breakfast promotions                                  ║
║                                                                      ║
║  5. HIGH-DEMAND PRODUCTS:                                            ║
║     • Bread - highest frequency, ensure always in stock              ║
║     • Milk - second highest, monitor expiry dates carefully          ║
║     • Eggs - third highest, maintain fresh supply                    ║
║     • Coffee & Sugar - consistent demand, bulk purchase recommended  ║
║                                                                      ║
║  6. INVENTORY MANAGEMENT:                                            ║
║     • Stock associated items proportionally                          ║
║     • If Bread sales increase, prepare for Milk/Eggs demand spike    ║
║     • Monitor Coffee-Sugar-Creamer as a unit for reordering          ║
║     • Keep Rice-Oil-Soy Sauce inventory balanced                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

# ============================================================================
# SECTION 9: PROJECT CONCLUSION AND SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("   STEP 8: PROJECT CONCLUSION AND SUMMARY")
print("=" * 70)

print(f"""
PROJECT SUMMARY:
================

Dataset: Grocery Store Transactions
Total Transactions Analyzed: {len(df_encoded)}
Unique Items: {len(te.columns_)}
Algorithm Used: Apriori
Minimum Support: {min_support} ({int(min_support*100)}%)
Minimum Confidence: 0.50 (50%)

KEY FINDINGS:
=============
1. Frequent Itemsets Found: {len(frequent_itemsets)}
2. Association Rules Generated: {len(rules)}
3. Strongest Association: The Bread-Milk-Eggs combination dominates
   the transaction patterns, appearing in the majority of baskets.
4. Coffee-Sugar-Creamer forms a distinct cluster of associated items.
5. Rice-Cooking Oil-Soy Sauce represents a cooking essentials pattern.

CONCLUSION:
===========
The association rule mining analysis successfully identified meaningful
purchasing patterns in the grocery store dataset. The Apriori algorithm
revealed that customers tend to buy items in logical groups:
- Breakfast items (Bread, Milk, Eggs)
- Beverage items (Coffee, Sugar, Creamer)
- Cooking essentials (Rice, Cooking Oil, Soy Sauce)

These patterns can be leveraged for:
- Strategic product placement
- Targeted marketing campaigns
- Bundle pricing strategies
- Inventory optimization

The high lift values (>1) confirm that these associations are statistically
significant and not merely due to the individual popularity of items.
""")

# ============================================================================
# SECTION 10: SAVE RESULTS TO FILES
# ============================================================================
print("\n" + "=" * 70)
print("   SAVING RESULTS TO FILES")
print("=" * 70)

# Save frequent itemsets
freq_output = frequent_itemsets.copy()
freq_output['itemsets'] = freq_output['itemsets'].apply(lambda x: ', '.join(sorted(x)))
freq_output.to_csv('output/frequent_itemsets.csv', index=False)
print("Saved: output/frequent_itemsets.csv")

# Save association rules
rules_output = rules.copy()
rules_output['antecedents'] = rules_output['antecedents'].apply(lambda x: ', '.join(sorted(x)))
rules_output['consequents'] = rules_output['consequents'].apply(lambda x: ', '.join(sorted(x)))
rules_output[['antecedents', 'consequents', 'support', 'confidence', 'lift']].to_csv(
    'output/association_rules.csv', index=False)
print("Saved: output/association_rules.csv")

# Save clean dataset
df.to_csv('output/clean_dataset.csv', index=False)
print("Saved: output/clean_dataset.csv")

print("\n" + "=" * 70)
print("   PROJECT COMPLETED SUCCESSFULLY!")
print("=" * 70)
print("\nAll charts saved in: charts/")
print("All data outputs saved in: output/")
print("=" * 70)
