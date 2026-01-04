"""
Process Megaline Call Data for Erlang C Staffing Analysis

Takes raw call data (user_id, call_date, duration) and transforms it into
hourly call volumes and average handle times for workforce planning.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def process_call_data(input_csv_path):
    """
    Process Megaline call data into hourly aggregates for Erlang C analysis.
    
    Input CSV columns: id, user_id, call_date, duration
    
    Returns:
    - DataFrame with hourly call volumes
    - Average handle time across all calls
    """
    
    print(f"Loading call data from: {input_csv_path}")
    
    # Load the data
    df = pd.read_csv(input_csv_path)
    
    print(f"Loaded {len(df):,} call records")
    print(f"Date range: {df['call_date'].min()} to {df['call_date'].max()}")
    
    # Convert call_date to datetime
    df['call_date'] = pd.to_datetime(df['call_date'])
    
    # Extract hour of day (0-23)
    df['hour'] = df['call_date'].dt.hour
    
    # Extract date (for daily patterns)
    df['date'] = df['call_date'].dt.date
    
    # Extract day of week (0=Monday, 6=Sunday)
    df['day_of_week'] = df['call_date'].dt.dayofweek
    
    # Calculate average handle time (AHT) in minutes
    aht_minutes = df['duration'].mean()
    aht_seconds = aht_minutes * 60
    
    print(f"\nAverage Handle Time (AHT): {aht_minutes:.2f} minutes ({aht_seconds:.0f} seconds)")
    
    # Aggregate calls by hour of day (across all dates)
    hourly_stats = df.groupby('hour').agg({
        'id': 'count',  # Number of calls
        'duration': 'mean'  # Average call duration
    }).rename(columns={'id': 'calls', 'duration': 'avg_duration_minutes'})
    
    # Add day of week breakdown (weekday vs weekend patterns)
    df['is_weekend'] = df['day_of_week'].isin([5, 6])  # Saturday=5, Sunday=6
    
    weekday_hourly = df[~df['is_weekend']].groupby('hour').agg({
        'id': 'count',
        'duration': 'mean'
    }).rename(columns={'id': 'calls_weekday', 'duration': 'avg_duration_weekday'})
    
    weekend_hourly = df[df['is_weekend']].groupby('hour').agg({
        'id': 'count',
        'duration': 'mean'
    }).rename(columns={'id': 'calls_weekend', 'duration': 'avg_duration_weekend'})
    
    # Combine into single dataframe
    hourly_combined = hourly_stats.join(weekday_hourly).join(weekend_hourly).fillna(0)
    
    # Calculate calls per hour (average across all days in dataset)
    num_days = (df['call_date'].max() - df['call_date'].min()).days + 1
    num_weekdays = df[~df['is_weekend']]['date'].nunique()
    num_weekend_days = df[df['is_weekend']]['date'].nunique()
    
    hourly_combined['calls_per_hour_avg'] = hourly_combined['calls'] / num_days
    hourly_combined['calls_per_hour_weekday'] = hourly_combined['calls_weekday'] / max(num_weekdays, 1)
    hourly_combined['calls_per_hour_weekend'] = hourly_combined['calls_weekend'] / max(num_weekend_days, 1)
    
    # Round for readability
    hourly_combined = hourly_combined.round(2)
    
    print(f"\nProcessed {num_days} days of data ({num_weekdays} weekdays, {num_weekend_days} weekend days)")
    print(f"\nHourly call volume summary:")
    print(f"  Peak hour: {hourly_combined['calls_per_hour_avg'].idxmax()}:00 ({hourly_combined['calls_per_hour_avg'].max():.1f} calls/hour)")
    print(f"  Low hour: {hourly_combined['calls_per_hour_avg'].idxmin()}:00 ({hourly_combined['calls_per_hour_avg'].min():.1f} calls/hour)")
    
    return hourly_combined, aht_minutes


def main():
    """Main execution function"""
    
    # Define paths
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Input file (adjust path as needed)
    input_file = project_root.parent / "Megaline-Telecom-Analytics" / "dataset" / "megaline_calls.csv"
    
    # Alternative: if running from within the Megaline project
    if not input_file.exists():
        input_file = project_root / "dataset" / "megaline_calls.csv"
    
    # Alternative: manual path specification
    if not input_file.exists():
        print("Please specify the path to megaline_calls.csv:")
        input_file = Path(input("Path: ").strip())
    
    if not input_file.exists():
        print(f"Error: Could not find {input_file}")
        return
    
    # Process the data
    hourly_data, aht = process_call_data(input_file)
    
    # Save outputs
    output_file = data_dir / "call_volume_hourly.csv"
    hourly_data.to_csv(output_file)
    print(f"\n✓ Saved hourly call volume data to: {output_file}")
    
    # Save AHT as a text file for reference
    aht_file = data_dir / "average_handle_time.txt"
    with open(aht_file, 'w') as f:
        f.write(f"Average Handle Time (AHT): {aht:.2f} minutes\n")
        f.write(f"Calculated from {len(pd.read_csv(input_file)):,} call records\n")
    print(f"✓ Saved AHT reference to: {aht_file}")
    
    print("\n" + "="*60)
    print("Data processing complete!")
    print("="*60)
    print(f"\nNext steps:")
    print(f"1. Review: {output_file}")
    print(f"2. Run: erlang_c_calculator.py")
    print(f"3. Create visualizations in staffing_analysis notebook")


if __name__ == "__main__":
    main()