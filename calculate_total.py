import json

# Read the JSON file
with open('june_expenses.json', 'r') as f:
    data = json.load(f)

total = 0
count = 0
transactions = []

print("June 2025 Expense Transactions:")
print("=" * 60)

# The data is directly an array of purchase transactions
for item in data:
    amount = float(item.get('totalAmt', 0))
    date = item.get('txnDate', 'N/A')
    memo = item.get('privateNote', item.get('memo', 'N/A'))
    
    # Get vendor name if available
    vendor = ""
    if item.get('entityRef'):
        vendor = item.get('entityRef', {}).get('name', 'Unknown')
    
    total += amount
    count += 1
    
    print(f"Date: {date[:10]}, Amount: ${amount:.2f}, Vendor: {vendor}")
    transactions.append({'date': date, 'amount': amount, 'memo': memo, 'vendor': vendor})

print("=" * 60)
print(f"TOTAL JUNE 2025 EXPENSES: ${total:.2f}")
print(f"NUMBER OF TRANSACTIONS: {count}")