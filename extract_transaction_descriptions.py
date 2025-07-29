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

print("Processing June 2025 Expense Transactions with Bank Descriptions...")
print("=" * 80)

# Process all transactions
for item in data:
    amount = float(item.get('totalAmt', 0))
    date = item.get('txnDate', 'N/A')
    
    # Get the actual bank transaction description from privateNote
    bank_description = item.get('privateNote')
    if not bank_description:
        bank_description = item.get('memo')
    if not bank_description:
        bank_description = 'No Description Available'
    
    # Get vendor name if available (for exclusion check)
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

# Write to file
with open('june_2025_bank_transactions_sorted.txt', 'w') as f:
    f.write("JUNE 2025 BANK TRANSACTIONS - FILTERED & SORTED BY AMOUNT\n")
    f.write("=" * 100 + "\n")
    f.write(f"Excluded vendors: {', '.join(excluded_vendors)}\n")
    f.write(f"Excluded amount: ${excluded_total:,.2f} ({excluded_count} transactions)\n")
    f.write("=" * 100 + "\n\n")
    f.write(f"TOTAL INCLUDED EXPENSES: ${total:,.2f}\n")
    f.write(f"NUMBER OF INCLUDED TRANSACTIONS: {count}\n")
    f.write("=" * 100 + "\n\n")
    
    for i, txn in enumerate(transactions, 1):
        f.write(f"{i:3d}. ${txn['amount']:>9,.2f} | {txn['date']} | {txn['description']}\n")
        f.write("     " + "-" * 120 + "\n")

# Display summary and top transactions
print(f"EXCLUDED VENDORS: {', '.join(excluded_vendors)}")
print(f"Excluded Total: ${excluded_total:,.2f} ({excluded_count} transactions)")
print()
print(f"FILTERED TOTAL: ${total:,.2f}")
print(f"FILTERED TRANSACTIONS: {count}")
print()
print("Top 15 Bank Transaction Descriptions (after filtering):")
print("=" * 80)
for i, txn in enumerate(transactions[:15], 1):
    description_preview = txn['description'][:70] + "..." if len(txn['description']) > 70 else txn['description']
    print(f"{i:2d}. ${txn['amount']:>9,.2f} | {txn['date']} | {description_preview}")

print()
print("Full list with bank descriptions saved to: june_2025_bank_transactions_sorted.txt")