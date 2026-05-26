# User Guide
## Association Rule Mining and Market Basket Analysis System

---

## Getting Started

### 1. Login
- Open http://127.0.0.1:5000 in your browser
- Enter username: `admin` and password: `admin123`
- Click "Login"

### 2. Upload a Dataset
- Click "Datasets" in the sidebar
- Click "Upload New Dataset"
- Enter a name (e.g., "Grocery Store Data")
- Select your CSV file
- Click "Upload Dataset"

**CSV Format Required:**
```
Transaction_ID,Items
T001,"Bread, Milk, Eggs"
T002,"Rice, Coffee, Sugar"
```

### 3. Preprocess Data
- Click "Preprocessing" in the sidebar
- Select your dataset
- Click "Process"
- Review the cleaning steps and results

### 4. Exploratory Data Analysis
- Click "EDA" in the sidebar
- Select your preprocessed dataset
- Click "Analyze"
- View item frequencies, charts, and heatmaps

### 5. Mine Frequent Itemsets
- Click "Frequent Itemsets" in the sidebar
- Select dataset and algorithm (Apriori or FP-Growth)
- Set minimum support (default: 0.20)
- Click "Run Mining Algorithm"
- View discovered frequent itemsets

### 6. Generate Association Rules
- Click "Association Rules" in the sidebar
- Configure parameters (support, confidence, lift)
- Click "Generate Rules"
- View rules table with metrics

### 7. View Visualizations
- Click "Visualizations" in the sidebar
- Select dataset
- Click "Generate Charts"
- View network graphs, scatter plots, correlation matrices

### 8. Get Recommendations
- Click "Recommendations" in the sidebar
- Select a mining result
- Click "Generate"
- View product bundles, cross-selling, store layout suggestions

### 9. Export Reports
- Click "Reports" in the sidebar
- Choose format: CSV, Excel, or PDF
- Click download button

---

## Understanding the Metrics

| Metric | Meaning | Example |
|--------|---------|---------|
| Support | How often items appear together | 0.30 = 30% of transactions |
| Confidence | How reliable the rule is | 0.80 = 80% of the time |
| Lift | Correlation strength | 2.0 = 2x more likely |

---

## Tips

- Start with default parameters (support=0.20, confidence=0.50)
- If too few results, lower the thresholds
- If too many results, raise the thresholds
- Focus on rules with high lift for strongest associations
- Use FP-Growth for larger datasets (faster)
- Use Apriori for smaller datasets (simpler)
