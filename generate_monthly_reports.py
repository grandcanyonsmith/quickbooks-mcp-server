import json
import subprocess
import os
from datetime import datetime

# Month configurations
months = [
    {"name": "January", "start": "2025-01-01", "end": "2025-01-31"},
    {"name": "February", "start": "2025-02-01", "end": "2025-02-28"},
    {"name": "March", "start": "2025-03-01", "end": "2025-03-31"},
    {"name": "April", "start": "2025-04-01", "end": "2025-04-30"},
    {"name": "May", "start": "2025-05-01", "end": "2025-05-31"},
    {"name": "June", "start": "2025-06-01", "end": "2025-06-30"},
    {"name": "July", "start": "2025-07-01", "end": "2025-07-31"},
    {"name": "August", "start": "2025-08-01", "end": "2025-08-31"},
    {"name": "September", "start": "2025-09-01", "end": "2025-09-30"},
    {"name": "October", "start": "2025-10-01", "end": "2025-10-31"},
    {"name": "November", "start": "2025-11-01", "end": "2025-11-30"},
    {"name": "December", "start": "2025-12-01", "end": "2025-12-31"}
]

# People to exclude
excluded_vendors = [
    "Stockton Walbeck", 
    "Dakota Walbeck", 
    "Parker Walbeck", 
    "Canyon Smith"
]

def get_month_data(start_date, end_date):
    """Query QuickBooks for month data"""
    cmd = [
        'curl', '-X', 'POST', 'http://localhost:8080/api/v1/quickbooks/query',
        '-H', 'Content-Type: application/json',
        '-d', f'{{"query": "SELECT * FROM Purchase WHERE TxnDate >= \'{start_date}\' AND TxnDate <= \'{end_date}\' ORDER BY TxnDate DESC"}}'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error querying data: {result.stderr}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def process_month_data(data, month_name):
    """Process and filter month data"""
    total = 0
    count = 0
    transactions = []
    excluded_total = 0
    excluded_count = 0

    for item in data:
        amount = float(item.get('totalAmt', 0))
        date = item.get('txnDate', 'N/A')
        
        # Get the actual bank transaction description
        bank_description = item.get('privateNote')
        if not bank_description:
            bank_description = item.get('memo')
        if not bank_description:
            bank_description = 'No Description Available'
        
        # Get vendor name for exclusion check
        vendor = ""
        if item.get('entityRef'):
            vendor = item.get('entityRef', {}).get('name', '')
        
        # Check if this vendor should be excluded
        if vendor in excluded_vendors:
            excluded_total += amount
            excluded_count += 1
            continue
        
        # Include this transaction
        total += amount
        count += 1
        
        transactions.append({
            'date': date[:10] if date != 'N/A' else 'N/A',
            'amount': amount,
            'vendor': vendor if vendor else 'No Vendor Listed',
            'description': bank_description[:200] if len(bank_description) > 200 else bank_description
        })

    # Sort transactions by amount (highest to lowest)
    transactions.sort(key=lambda x: x['amount'], reverse=True)
    
    return {
        'transactions': transactions,
        'total': total,
        'count': count,
        'excluded_total': excluded_total,
        'excluded_count': excluded_count
    }

def write_month_report(month_data, month_name, folder_path):
    """Write month report to file"""
    filename = f"{folder_path}/{month_name.lower()}_bank_transactions_sorted.txt"
    
    with open(filename, 'w') as f:
        f.write(f"{month_name.upper()} 2025 BANK TRANSACTIONS - FILTERED & SORTED BY AMOUNT\n")
        f.write("=" * 100 + "\n")
        f.write(f"Excluded vendors: {', '.join(excluded_vendors)}\n")
        f.write(f"Excluded amount: ${month_data['excluded_total']:,.2f} ({month_data['excluded_count']} transactions)\n")
        f.write("=" * 100 + "\n\n")
        
        if month_data['transactions']:
            for i, txn in enumerate(month_data['transactions'], 1):
                f.write(f"{i:3d}. ${txn['amount']:>9,.2f} | {txn['date']} | {txn['description']}\n")
                f.write("     " + "-" * 120 + "\n")
        else:
            f.write("No transactions found for this month.\n")
    
    return filename

# Generate reports for all months
print("Generating monthly expense reports for 2025...")
print("=" * 80)

summary_data = []

for month in months:
    print(f"Processing {month['name']} 2025...")
    
    # Get data for this month
    data = get_month_data(month['start'], month['end'])
    
    if data:
        # Process the data
        month_data = process_month_data(data, month['name'])
        
        # Write the report
        folder_path = f"2025-expenses/{month['name']}"
        filename = write_month_report(month_data, month['name'], folder_path)
        
        # Store summary info
        summary_data.append({
            'month': month['name'],
            'total': month_data['total'],
            'count': month_data['count'],
            'excluded_total': month_data['excluded_total'],
            'excluded_count': month_data['excluded_count'],
            'filename': filename
        })
        
        print(f"  ✓ {month['name']}: ${month_data['total']:,.2f} ({month_data['count']} transactions)")
        if month_data['excluded_total'] > 0:
            print(f"    Excluded: ${month_data['excluded_total']:,.2f} ({month_data['excluded_count']} transactions)")
    else:
        print(f"  ✗ {month['name']}: No data available")
        summary_data.append({
            'month': month['name'],
            'total': 0,
            'count': 0,
            'excluded_total': 0,
            'excluded_count': 0,
            'filename': 'No file generated'
        })

# Generate summary report
print("\n" + "=" * 80)
print("ANNUAL SUMMARY (Filtered Totals)")
print("=" * 80)

annual_total = 0
annual_count = 0
annual_excluded_total = 0
annual_excluded_count = 0

for summary in summary_data:
    annual_total += summary['total']
    annual_count += summary['count']
    annual_excluded_total += summary['excluded_total']
    annual_excluded_count += summary['excluded_count']
    
    print(f"{summary['month']:<12}: ${summary['total']:>10,.2f} ({summary['count']:>3d} transactions)")

print("=" * 80)
print(f"{'TOTAL':<12}: ${annual_total:>10,.2f} ({annual_count:>3d} transactions)")
print(f"{'EXCLUDED':<12}: ${annual_excluded_total:>10,.2f} ({annual_excluded_count:>3d} transactions)")
print(f"{'GRAND TOTAL':<12}: ${annual_total + annual_excluded_total:>10,.2f} ({annual_count + annual_excluded_count:>3d} transactions)")

# Write annual summary to file
with open('2025-expenses/annual_summary.txt', 'w') as f:
    f.write("2025 ANNUAL EXPENSE SUMMARY\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Excluded vendors: {', '.join(excluded_vendors)}\n\n")
    
    for summary in summary_data:
        f.write(f"{summary['month']:<12}: ${summary['total']:>10,.2f} ({summary['count']:>3d} transactions)\n")
        if summary['excluded_total'] > 0:
            f.write(f"{'  Excluded':<12}: ${summary['excluded_total']:>10,.2f} ({summary['excluded_count']:>3d} transactions)\n")
    
    f.write("=" * 50 + "\n")
    f.write(f"{'TOTAL':<12}: ${annual_total:>10,.2f} ({annual_count:>3d} transactions)\n")
    f.write(f"{'EXCLUDED':<12}: ${annual_excluded_total:>10,.2f} ({annual_excluded_count:>3d} transactions)\n")
    f.write(f"{'GRAND TOTAL':<12}: ${annual_total + annual_excluded_total:>10,.2f} ({annual_count + annual_excluded_count:>3d} transactions)\n")

print(f"\nAnnual summary saved to: 2025-expenses/annual_summary.txt")
print("All monthly reports completed!")