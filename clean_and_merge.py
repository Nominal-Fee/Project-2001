import pandas as pd
import sqlite3
import os

def main():
    # Define file paths
    customer_file = os.path.join('data', 'customer.txt')
    order_file = os.path.join('data', 'order.txt')
    db_file = 'merged_database.sqlite'

    # Read data files
    print("Reading data...")
    try:
        customers = pd.read_csv(customer_file)
        orders = pd.read_csv(order_file)
    except FileNotFoundError as e:
        print(f"Error reading file: {e}")
        return

    # Clean duplicate entries
    print("Removing duplicates...")
    customers.drop_duplicates(inplace=True)
    orders.drop_duplicates(inplace=True)

    # Conversion logic
    print("Converting amounts to CNY...")
    rates = {
        'USD': 6.9,
        'EUR': 7.5,
        'CNY': 1.0,
        'JPY': 0.05
    }
    
    orders['amount_cny'] = orders['amount'] * orders['currency'].map(rates)

    # Connect the order and customer data
    print("Merging data on customer_id...")
    merged_df = pd.merge(orders, customers, on='customer_id', how='left')

    # Connect to SQLite database
    print(f"Writing to SQLite database {db_file}...")
    conn = sqlite3.connect(db_file)

    # Write merged data
    merged_df.to_sql('merged_data', conn, if_exists='replace', index=False)

    # Create summary table (average amount_cny by region)
    print("Creating summary table...")
    summary_df = merged_df.groupby('region')['amount_cny'].mean().reset_index()
    summary_df.rename(columns={'amount_cny': 'average_amount_cny'}, inplace=True)

    # Save summary table to the database
    summary_df.to_sql('region_summary', conn, if_exists='replace', index=False)

    conn.close()
    print("Processing completed successfully.")

if __name__ == "__main__":
    main()
