import json
import subprocess
import re
from datetime import datetime
from collections import defaultdict

def get_month_data(start_date, end_date):
    """Get month data from QuickBooks"""
    cmd = [
        'curl', '-X', 'POST', 'http://localhost:8080/api/v1/quickbooks/query',
        '-H', 'Content-Type: application/json',
        '-d', f'{{"query": "SELECT * FROM Purchase WHERE TxnDate >= \'{start_date}\' AND TxnDate <= \'{end_date}\' MAXRESULTS 1000"}}'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return []
    except Exception as e:
        return []

def process_transactions(data):
    """Process and clean transaction data"""
    excluded_vendors = ["Stockton Walbeck", "Dakota Walbeck", "Parker Walbeck", "Canyon Smith"]
    transactions = []
    
    for item in data:
        amount = float(item.get('totalAmt', 0))
        date = item.get('txnDate', 'N/A')
        description = item.get('privateNote', item.get('memo', 'No Description Available'))
        
        vendor = ""
        if item.get('entityRef'):
            vendor = item.get('entityRef', {}).get('name', '')
        
        # Skip excluded vendors
        if vendor in excluded_vendors:
            continue
        
        transactions.append({
            'date': date[:10] if date != 'N/A' else 'N/A',
            'amount': amount,
            'description': description if description else 'No Description Available',
            'vendor': vendor if vendor else 'No Vendor Listed'
        })
    
    return transactions

# SORTING FUNCTIONS
def sort_by_amount(transactions, reverse=True):
    """Sort by transaction amount"""
    return sorted(transactions, key=lambda x: x['amount'], reverse=reverse)

def sort_by_date(transactions, reverse=True):
    """Sort by date (newest first by default)"""
    return sorted(transactions, key=lambda x: x['date'], reverse=reverse)

def sort_by_vendor(transactions):
    """Sort alphabetically by vendor"""
    return sorted(transactions, key=lambda x: x['vendor'])

def sort_by_description_keyword(transactions, keyword):
    """Sort by transactions containing specific keyword"""
    keyword_upper = keyword.upper()
    keyword_transactions = [t for t in transactions if keyword_upper in t['description'].upper()]
    other_transactions = [t for t in transactions if keyword_upper not in t['description'].upper()]
    return keyword_transactions + other_transactions

# ANALYSIS FUNCTIONS
def find_recurring_expenses(transactions):
    """Identify potentially recurring expenses"""
    vendor_patterns = defaultdict(list)
    
    for txn in transactions:
        # Group by vendor or by description patterns
        key = txn['vendor'] if txn['vendor'] != 'No Vendor Listed' else txn['description'][:50]
        vendor_patterns[key].append(txn)
    
    recurring = {}
    for vendor, txns in vendor_patterns.items():
        if len(txns) >= 2:  # Appears 2+ times
            amounts = [t['amount'] for t in txns]
            avg_amount = sum(amounts) / len(amounts)
            recurring[vendor] = {
                'count': len(txns),
                'total': sum(amounts),
                'average': avg_amount,
                'transactions': sorted(txns, key=lambda x: x['date'])
            }
    
    return dict(sorted(recurring.items(), key=lambda x: x[1]['total'], reverse=True))

def find_large_transactions(transactions, threshold=1000):
    """Find transactions over a certain threshold"""
    return [t for t in transactions if t['amount'] >= threshold]

def analyze_spending_patterns(transactions):
    """Analyze spending patterns and trends"""
    monthly_totals = defaultdict(float)
    daily_totals = defaultdict(float)
    vendor_totals = defaultdict(float)
    
    for txn in transactions:
        if txn['date'] != 'N/A':
            month_key = txn['date'][:7]  # YYYY-MM
            monthly_totals[month_key] += txn['amount']
            daily_totals[txn['date']] += txn['amount']
        
        vendor_totals[txn['vendor']] += txn['amount']
    
    return {
        'monthly': dict(monthly_totals),
        'daily': dict(daily_totals),
        'vendors': dict(sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True))
    }

def generate_sorting_report(month_name, start_date, end_date):
    """Generate comprehensive sorting and analysis report"""
    print(f"\n🔄 ADVANCED SORTING & ANALYSIS - {month_name.upper()} 2025")
    print("=" * 80)
    
    # Get data
    data = get_month_data(start_date, end_date)
    if not data:
        print("No data available")
        return
    
    transactions = process_transactions(data)
    total_amount = sum(t['amount'] for t in transactions)
    
    print(f"Total Transactions: {len(transactions)}")
    print(f"Total Amount: ${total_amount:,.2f}")
    print("=" * 80)
    
    # 1. TOP 10 BY AMOUNT
    print(f"\n💰 TOP 10 LARGEST TRANSACTIONS:")
    top_10 = sort_by_amount(transactions)[:10]
    for i, txn in enumerate(top_10, 1):
        print(f"{i:2d}. ${txn['amount']:>8,.2f} | {txn['date']} | {txn['description'][:60]}...")
    
    # 2. RECURRING EXPENSES
    print(f"\n🔄 RECURRING EXPENSES (2+ occurrences):")
    recurring = find_recurring_expenses(transactions)
    for vendor, data in list(recurring.items())[:10]:
        print(f"• {vendor[:40]}...")
        print(f"  Count: {data['count']} | Total: ${data['total']:,.2f} | Avg: ${data['average']:,.2f}")
    
    # 3. LARGE TRANSACTIONS (>$1000)
    large_txns = find_large_transactions(transactions, 1000)
    print(f"\n🚨 LARGE TRANSACTIONS (>${1000:,}+): {len(large_txns)} found")
    for txn in large_txns[:5]:
        print(f"• ${txn['amount']:,.2f} | {txn['date']} | {txn['description'][:50]}...")
    
    # 4. VENDOR ANALYSIS
    patterns = analyze_spending_patterns(transactions)
    print(f"\n🏪 TOP VENDORS BY SPENDING:")
    for vendor, amount in list(patterns['vendors'].items())[:10]:
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
        print(f"• {vendor[:40]:<40} ${amount:>8,.2f} ({percentage:4.1f}%)")
    
    # 5. SORTING DEMONSTRATIONS
    print(f"\n📊 SORTING EXAMPLES:")
    
    # Software-related expenses
    software_txns = sort_by_description_keyword(transactions, "SOFTWARE")
    software_total = sum(t['amount'] for t in software_txns if "SOFTWARE" in t['description'].upper())
    print(f"• Software-related expenses: ${software_total:,.2f}")
    
    # HighLevel expenses
    highlevel_txns = sort_by_description_keyword(transactions, "HIGHLEVEL")
    highlevel_total = sum(t['amount'] for t in highlevel_txns if "HIGHLEVEL" in t['description'].upper())
    print(f"• HighLevel expenses: ${highlevel_total:,.2f}")
    
    # PayPal transactions
    paypal_txns = sort_by_description_keyword(transactions, "PAYPAL")
    paypal_total = sum(t['amount'] for t in paypal_txns if "PAYPAL" in t['description'].upper())
    print(f"• PayPal transactions: ${paypal_total:,.2f}")
    
    return {
        'transactions': transactions,
        'recurring': recurring,
        'patterns': patterns,
        'large_transactions': large_txns
    }

# RULE SUGGESTIONS
def suggest_categorization_rules(transactions):
    """Suggest automated categorization rules based on patterns"""
    print(f"\n🎯 SUGGESTED CATEGORIZATION RULES:")
    print("=" * 50)
    
    # Analyze common patterns
    vendors = defaultdict(float)
    keywords = defaultdict(float)
    
    for txn in transactions:
        if txn['vendor'] != 'No Vendor Listed':
            vendors[txn['vendor']] += txn['amount']
        
        # Extract keywords from descriptions
        description_words = re.findall(r'\b[A-Z]{3,}\b', txn['description'].upper())
        for word in description_words:
            keywords[word] += txn['amount']
    
    print("📋 AUTO-CATEGORIZATION RULES:")
    print("1. IF vendor contains 'HIGHLEVEL' → Software & SaaS")
    print("2. IF description contains 'PAYPAL' → Affiliate Commissions")
    print("3. IF vendor = 'WISE INC' → VA & Contractors")
    print("4. IF description contains 'DADGUMMARKETING' → Marketing & Ads")
    print("5. IF amount > $5000 → Flag for Manual Review")
    
    print(f"\n🔍 TOP SPENDING PATTERNS TO MONITOR:")
    for vendor, amount in sorted(vendors.items(), key=lambda x: x[1], reverse=True)[:5]:
        if amount > 1000:
            print(f"• {vendor}: ${amount:,.2f}")

# Run analysis for June
if __name__ == "__main__":
    june_analysis = generate_sorting_report("June", "2025-06-01", "2025-06-30")
    
    if june_analysis:
        suggest_categorization_rules(june_analysis['transactions'])
        
        print(f"\n\n🛠️  ADDITIONAL SORTING OPTIONS YOU CAN USE:")
        print("1. `sort_by_amount(transactions, reverse=False)` - Smallest to largest")
        print("2. `sort_by_date(transactions, reverse=False)` - Oldest to newest") 
        print("3. `sort_by_vendor(transactions)` - Alphabetical by vendor")
        print("4. `sort_by_description_keyword(transactions, 'keyword')` - Filter by keyword")
        print("5. `find_large_transactions(transactions, 500)` - Custom threshold")
        print("6. `find_recurring_expenses(transactions)` - Identify patterns")