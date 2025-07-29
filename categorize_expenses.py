import json
import subprocess
import re
from collections import defaultdict

# Categorization Rules
EXPENSE_CATEGORIES = {
    'Software & SaaS': {
        'keywords': ['HIGHLEVEL', 'EXTENDLY', 'GOOGLE', 'USERPILOT', 'CHARGEFLOW', 'ONLINEJOBSPH', 'PADDLE', 'BB9 LLC', 'OPENAI', 'ADOBE', 'RAPIDAPI', 'X CORP'],
        'patterns': [r'GSUITE', r'CHATGPT', r'PREMIERE', r'SOFTWARE'],
        'description': 'Software subscriptions, SaaS tools, and digital services'
    },
    
    'VA & Contractors': {
        'keywords': ['WISE INC', 'PAYONEER', 'COURSE CREATOR PRO INC'],
        'patterns': [r'First half paym', r'Pay To:', r'WISE.*240517'],
        'description': 'Virtual assistants and contractor payments'
    },
    
    'Affiliate Commissions': {
        'keywords': ['PAYPAL'],
        'patterns': [r'PAYPAL \*[A-Z]+', r'ORTHOPATIE', r'ACADEMYVIS', r'PROFAMILY', r'TRAVELMONE', r'RENTALPROP', r'PAYNEPOINT', r'INEEDSCIEN'],
        'description': 'Affiliate and commission payments'
    },
    
    'Marketing & Ads': {
        'keywords': ['DADGUMMARKETING', 'FACEBOOK'],
        'patterns': [r'FACEBOOK\.COM', r'MARKETING'],
        'description': 'Advertising and marketing expenses'
    },
    
    'Contract Labor': {
        'keywords': ['JACKSON CRANDALL', 'May Commissions'],
        'patterns': [r'Commissions?', r'Contract.*labor'],
        'description': 'Contract labor and commission payments'
    },
    
    'Tax Payments': {
        'keywords': ['IRS', 'TAX PAYMNT', 'USATAXPYMT'],
        'patterns': [r'TAX', r'IRS.*USATAXPYMT'],
        'description': 'Tax payments and government fees'
    },
    
    'Bank & Financial': {
        'keywords': ['INST XFER', 'CURRENTDIGI'],
        'patterns': [r'INST XFER', r'TRANSFER'],
        'description': 'Bank transfers and financial services'
    },
    
    'Business Services': {
        'keywords': ['AMAZON'],
        'patterns': [r'BUSINESS.*SERVICES'],
        'description': 'General business services and supplies'
    }
}

def categorize_transaction(description, amount):
    """Categorize a transaction based on description and amount"""
    if not description:
        return 'Other/Miscellaneous'
        
    description_upper = description.upper()
    
    for category, rules in EXPENSE_CATEGORIES.items():
        # Check keywords
        if any(keyword in description_upper for keyword in rules['keywords']):
            return category
            
        # Check patterns
        if any(re.search(pattern, description_upper) for pattern in rules['patterns']):
            return category
    
    return 'Other/Miscellaneous'

def get_month_data_with_categories(start_date, end_date):
    """Get month data and categorize it"""
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
        print(f"Error: {e}")
        return []

def analyze_expenses_by_category(data, month_name):
    """Analyze and categorize expenses"""
    excluded_vendors = ["Stockton Walbeck", "Dakota Walbeck", "Parker Walbeck", "Canyon Smith"]
    
    categories = defaultdict(lambda: {'total': 0, 'count': 0, 'transactions': []})
    excluded_total = 0
    excluded_count = 0
    
    for item in data:
        amount = float(item.get('totalAmt', 0))
        date = item.get('txnDate', 'N/A')[:10]
        
        # Get description
        description = item.get('privateNote', item.get('memo', 'No Description Available'))
        
        # Get vendor for exclusion check
        vendor = ""
        if item.get('entityRef'):
            vendor = item.get('entityRef', {}).get('name', '')
        
        # Skip excluded vendors
        if vendor in excluded_vendors:
            excluded_total += amount
            excluded_count += 1
            continue
        
        # Categorize transaction
        category = categorize_transaction(description, amount)
        
        categories[category]['total'] += amount
        categories[category]['count'] += 1
        safe_description = description if description else 'No Description Available'
        categories[category]['transactions'].append({
            'date': date,
            'amount': amount,
            'description': safe_description[:100] + ('...' if len(safe_description) > 100 else ''),
            'vendor': vendor if vendor else 'No Vendor'
        })
    
    return dict(categories), excluded_total, excluded_count

def generate_category_report(month_name, start_date, end_date):
    """Generate a categorized expense report for a month"""
    print(f"\nProcessing {month_name} 2025 with smart categorization...")
    
    data = get_month_data_with_categories(start_date, end_date)
    if not data:
        print(f"No data available for {month_name}")
        return None
    
    categories, excluded_total, excluded_count = analyze_expenses_by_category(data, month_name)
    
    # Sort categories by total spending
    sorted_categories = sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True)
    
    total_spending = sum(cat['total'] for cat in categories.values())
    
    print(f"\n📊 {month_name.upper()} 2025 - EXPENSE ANALYSIS BY CATEGORY")
    print("=" * 80)
    print(f"Total Spending (Filtered): ${total_spending:,.2f}")
    print(f"Excluded: ${excluded_total:,.2f} ({excluded_count} transactions)")
    print("=" * 80)
    
    for category, data in sorted_categories:
        percentage = (data['total'] / total_spending * 100) if total_spending > 0 else 0
        print(f"\n🏷️  {category}")
        print(f"   Amount: ${data['total']:,.2f} ({percentage:.1f}%)")
        print(f"   Transactions: {data['count']}")
        print(f"   Average: ${data['total']/data['count']:,.2f}" if data['count'] > 0 else "   Average: $0.00")
        
        # Show top 3 transactions for this category
        top_transactions = sorted(data['transactions'], key=lambda x: x['amount'], reverse=True)[:3]
        for i, txn in enumerate(top_transactions, 1):
            print(f"   {i}. ${txn['amount']:,.2f} - {txn['description']}")
    
    return {
        'month': month_name,
        'categories': dict(categories),
        'total': total_spending,
        'excluded_total': excluded_total,
        'sorted_categories': sorted_categories
    }

# Demonstration: Analyze June 2025
if __name__ == "__main__":
    print("🔍 SMART EXPENSE CATEGORIZATION SYSTEM")
    print("=" * 60)
    print("\n📋 Available Categories:")
    for category, rules in EXPENSE_CATEGORIES.items():
        print(f"• {category}: {rules['description']}")
    
    # Analyze June as an example
    june_analysis = generate_category_report("June", "2025-06-01", "2025-06-30")
    
    print(f"\n\n💡 SORTING OPTIONS AVAILABLE:")
    print("1. By Amount (Highest to Lowest) - Current default")
    print("2. By Date (Newest to Oldest)")
    print("3. By Category (Alphabetical)")
    print("4. By Transaction Count per Category")
    print("5. By Average Transaction Size")
    print("6. By Vendor/Service Provider")
    
    print(f"\n🎯 RECOMMENDED CATEGORIZATION RULES:")
    print("1. Set up recurring categorization for known vendors")
    print("2. Create alerts for transactions over $1,000")
    print("3. Track software subscriptions separately")
    print("4. Monitor affiliate/commission patterns")
    print("5. Separate one-time vs recurring expenses")