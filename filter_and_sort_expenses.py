import json

# Read the JSON file
with open('june_expenses.json', 'r') as f:
    data = json.load(f)

# People to exclude
excluded_vendors = [
    "Stockton Walbeck", 
    "Dakota Walbeck", 
    "Parker Walbeck", 
    "Canyon Smith"
]

total = 0
count = 0
transactions = []
excluded_total = 0
excluded_count = 0

print("Processing June 2025 Expense Transactions...")
print("=" * 60)

# Process all transactions
for item in data:
    amount = float(item.get('totalAmt', 0))
    date = item.get('txnDate', 'N/A')
    memo = item.get('privateNote', item.get('memo', 'N/A'))
    
    # Get vendor name if available
    vendor = ""
    if item.get('entityRef'):
        vendor = item.get('entityRef', {}).get('name', 'Unknown')
    
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
        'vendor': vendor if vendor else 'No Vendor',
        'memo': memo[:100] if memo and memo != 'N/A' else 'No Memo'
    })

# Sort transactions by amount (highest to lowest)
transactions.sort(key=lambda x: x['amount'], reverse=True)

# Write to file
with open('june_2025_expenses_filtered_sorted.txt', 'w') as f:
    f.write("JUNE 2025 EXPENSES - FILTERED & SORTED BY AMOUNT\n")
    f.write("=" * 80 + "\n")
    f.write(f"Excluded vendors: {', '.join(excluded_vendors)}\n")
    f.write(f"Excluded amount: ${excluded_total:,.2f} ({excluded_count} transactions)\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"TOTAL INCLUDED EXPENSES: ${total:,.2f}\n")
    f.write(f"NUMBER OF INCLUDED TRANSACTIONS: {count}\n")
    f.write("=" * 80 + "\n\n")
    
    for i, txn in enumerate(transactions, 1):
        line = f"{i:3d}. ${txn['amount']:>8,.2f} | {txn['date']} | {txn['vendor'][:30]:<30} | {txn['memo'][:40]}\n"
        f.write(line)

# Display summary
print(f"EXCLUDED VENDORS:")
for vendor in excluded_vendors:
    print(f"  - {vendor}")
print(f"Excluded Total: ${excluded_total:,.2f} ({excluded_count} transactions)")
print()
print(f"FILTERED TOTAL: ${total:,.2f}")
print(f"FILTERED TRANSACTIONS: {count}")
print()
print("Top 10 Expenses (after filtering):")
print("-" * 60)
for i, txn in enumerate(transactions[:10], 1):
    print(f"{i:2d}. ${txn['amount']:>8,.2f} | {txn['date']} | {txn['vendor'][:25]}")

print()
print("Full sorted list saved to: june_2025_expenses_filtered_sorted.txt")