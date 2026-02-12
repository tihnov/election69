"""
Data Relation on Constituency Level

This file creates a relation between constituency and the candidate and party on each constituency.
The relation is stored in a json file and xlsx file in the data folder.
The base data is info_constituency.json and add data from stats_cons.json which related by cons_id.

Fields included:
- From info_constituency.json: cons_id, cons_no, prov_id, total_vote_stations, registered_vote
- From stats_cons.json: turn_out, valid_votes, invalid_votes, blank_votes, party_list_turn_out,
  party_list_valid_votes, party_list_invalid_votes, party_list_blank_votes,
  sum of mp_app_vote in candidates, sum of party_list_vote in result_party
"""

import json
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def load_json_file(file_path):
    """Load JSON file and return data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_constituency_stats(cons_id, stats_data):
    """Find constituency statistics from stats_cons.json by cons_id"""
    # Navigate through result_province -> constituencies
    for province in stats_data.get('result_province', []):
        for constituency in province.get('constituencies', []):
            if constituency.get('cons_id') == cons_id:
                return constituency
    return None


def calculate_total_mp_votes(candidates):
    """Calculate sum of all mp_app_vote in candidates list"""
    return sum(candidate.get('mp_app_vote', 0) for candidate in candidates)


def calculate_total_party_list_votes(result_party):
    """Calculate sum of all party_list_vote in result_party list"""
    return sum(party.get('party_list_vote', 0) for party in result_party)

def create_constituency_relation():
    """Create dataframe relating constituency data with statistics"""
    
    # Define file paths
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    
    info_constituency_path = data_dir / 'info_constituency.json'
    stats_cons_path = data_dir / 'stats_cons.json'
    
    # Load data
    print("Loading data files...")
    info_constituency = load_json_file(info_constituency_path)
    stats_cons = load_json_file(stats_cons_path)
    
    # Create list to store combined data
    combined_data = []
    
    print("Processing constituencies...")
    for constituency in info_constituency:
        cons_id = constituency.get('cons_id')
        
        # Get base data from info_constituency.json
        cons_data = {
            'cons_id': cons_id,
            'cons_no': constituency.get('cons_no'),
            'prov_id': constituency.get('prov_id'),
            'total_vote_stations': constituency.get('total_vote_stations'),
            'registered_vote': constituency.get('registered_vote')
        }
        
        # Find matching statistics
        stats = find_constituency_stats(cons_id, stats_cons)
        
        if stats:
            # Add statistics data
            cons_data.update({
                'turn_out': stats.get('turn_out'),
                'valid_votes': stats.get('valid_votes'),
                'invalid_votes': stats.get('invalid_votes'),
                'blank_votes': stats.get('blank_votes'),
                'party_list_turn_out': stats.get('party_list_turn_out'),
                'party_list_valid_votes': stats.get('party_list_valid_votes'),
                'party_list_invalid_votes': stats.get('party_list_invalid_votes'),
                'party_list_blank_votes': stats.get('party_list_blank_votes'),
                'total_mp_app_votes': calculate_total_mp_votes(stats.get('candidates', [])),
                'total_party_list_votes': calculate_total_party_list_votes(stats.get('result_party', []))
            })
        else:
            # No stats found, fill with None
            cons_data.update({
                'turn_out': None,
                'valid_votes': None,
                'invalid_votes': None,
                'blank_votes': None,
                'party_list_turn_out': None,
                'party_list_valid_votes': None,
                'party_list_invalid_votes': None,
                'party_list_blank_votes': None,
                'total_mp_app_votes': None,
                'total_party_list_votes': None
            })
        
        combined_data.append(cons_data)
    
    # Create DataFrame
    df = pd.DataFrame(combined_data)
    
    # Sort by prov_id and cons_no
    df = df.sort_values(['prov_id', 'cons_no']).reset_index(drop=True)
    
    print(f"Processed {len(df)} constituencies")
    
    df['total_mp_app_votes_diff'] = df['total_mp_app_votes'] - df['valid_votes']

    df['total_party_list_votes_diff'] = df['total_party_list_votes'] - df['party_list_valid_votes']

    df['total_mp_turnout_diff'] = df['turn_out'] - (df['total_mp_app_votes'] + df['invalid_votes'] + df['blank_votes'])

    df['total_party_turnout_diff'] = df['party_list_turn_out'] - (df['total_party_list_votes'] + df['party_list_invalid_votes'] + df['party_list_blank_votes'])

    df['mp_party_diff'] = (df['total_mp_app_votes'] + df['invalid_votes'] + df['blank_votes']) - (df['total_party_list_votes'] + df['party_list_invalid_votes'] + df['party_list_blank_votes'])

    df['registered_per_station'] = df['registered_vote'] / df['total_vote_stations']

    df['registered_mp_turnout_ratio'] = (df['total_mp_app_votes'] + df['invalid_votes'] + df['blank_votes']) / df['registered_vote']

    df['registered_party_turnout_ratio'] = (df['total_party_list_votes'] + df['party_list_invalid_votes'] + df['party_list_blank_votes']) / df['registered_vote']

    df['mp_party_error_per_station'] = df['mp_party_diff'] / df['total_vote_stations']
    # Save to JSON
    output_json_path = data_dir / 'relation_constituency.json'
    print(f"Saving to {output_json_path}...")
    df.to_json(output_json_path, orient='records', force_ascii=False, indent=2)
    
    # Save to Excel
    output_xlsx_path = data_dir / 'relation_constituency.xlsx'
    print(f"Saving to {output_xlsx_path}...")
    df.to_excel(output_xlsx_path, index=False, sheet_name='Constituencies')
    
    print("Done!")
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    return df


if __name__ == "__main__":
    df = create_constituency_relation()
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Create histogram of mp_party_diff
    print("\nCreating histogram of mp_party_diff...")
    
    # Define bins from -12000 to 12000 with width of 2000
    bins = np.arange(-12000, 13000, 200)
    
    # Create the histogram
    plt.figure(figsize=(12, 6))
    counts, bin_edges, patches = plt.hist(df['mp_party_diff'].dropna(), bins=bins, edgecolor='black', alpha=0.7)
    
    # Add value labels on top of each bar
    for i, (count, patch) in enumerate(zip(counts, patches)):
        if count > 0:  # Only show label if count is not zero
            height = patch.get_height()
            plt.text(patch.get_x() + patch.get_width()/2., height,
                    f'{int(count)}',
                    ha='center', va='bottom', fontsize=8, rotation=0)
    
    plt.xlabel('MP-Party Difference', fontsize=12)
    plt.ylabel('Count of Constituencies', fontsize=12)
    plt.title('Distribution of MP-Party Vote Difference by Constituency', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Add vertical line at 0
    plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero difference')
    plt.legend()
    
    # Save the plot
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    plot_path = data_dir / 'mp_party_diff_histogram.png'
    plt.savefig(plot_path, dpi=600, bbox_inches='tight')
    print(f"Histogram saved to {plot_path}")
    
    # Show the plot
    plt.show()
    
    # Print statistics
    print("\nStatistics for mp_party_diff:")
    print(df['mp_party_diff'].describe()) 

    # Create histogram of mp_party_error_per_station
    print("\nCreating histogram of mp_party_error_per_station...")
    
    # Define bins from -12000 to 12000 with width of 2000
    bins = np.arange(-30, 50, 1)
    
    # Create the histogram
    plt.figure(figsize=(12, 6))
    counts, bin_edges, patches = plt.hist(df['mp_party_error_per_station'].dropna(), bins=bins, edgecolor='black', alpha=0.7)
    
    # Add value labels on top of each bar
    for i, (count, patch) in enumerate(zip(counts, patches)):
        if count > 0:  # Only show label if count is not zero
            height = patch.get_height()
            plt.text(patch.get_x() + patch.get_width()/2., height,
                    f'{int(count)}',
                    ha='center', va='bottom', fontsize=8, rotation=0)
    
    plt.xlabel('MP-Party Error Per Station', fontsize=12)
    plt.ylabel('Count of Constituencies', fontsize=12)
    plt.title('Distribution of MP-Party Error Per Station by Constituency', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Add vertical line at 0
    plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero difference')
    plt.legend()
    
    # Save the plot
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    plot_path = data_dir / 'mp_party_error_per_station_histogram.png'
    plt.savefig(plot_path, dpi=600, bbox_inches='tight')
    print(f"Histogram saved to {plot_path}")
    
    # Show the plot
    plt.show()
    
    # Print statistics
    print("\nStatistics for mp_party_error_per_station:")
    print(df['mp_party_error_per_station'].describe()) 

    dfofInterest = df[df['mp_party_error_per_station'].abs() > 3]
    print(f"\nConstituencies with |mp_party_error_per_station| > 3: {len(dfofInterest)}")
    # Save to JSON
    output_json_path = data_dir / 'interest_constituency.json'
    print(f"Saving to {output_json_path}...")
    dfofInterest.to_json(output_json_path, orient='records', force_ascii=False, indent=2)
    
    # Save to Excel
    output_xlsx_path = data_dir / 'interest_constituency.xlsx'
    print(f"Saving to {output_xlsx_path}...")
    dfofInterest.to_excel(output_xlsx_path, index=False, sheet_name='Constituencies')
    
    # Create plot of mp_party_diff for constituencies of interest (sorted max to min)
    if len(dfofInterest) > 0:
        print("\nCreating mp_party_diff plot for constituencies of interest...")
        
        # Sort by mp_party_diff from max to min
        dfofInterest_sorted = dfofInterest.sort_values('mp_party_diff', ascending=False)
        
        # Create the plot
        plt.figure(figsize=(16, 8))
        bars = plt.bar(range(len(dfofInterest_sorted)), dfofInterest_sorted['mp_party_diff'], 
                edgecolor='black', alpha=0.7)
        
        # Add value labels on top of each bar
        for i, (bar, value) in enumerate(zip(bars, dfofInterest_sorted['mp_party_diff'])):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(value)}',
                    ha='center', va='bottom' if height >= 0 else 'top', 
                    fontsize=7, rotation=0)
        
        # Set x-axis labels
        plt.xticks(range(len(dfofInterest_sorted)), dfofInterest_sorted['cons_id'], 
                   rotation=90, fontsize=8)
        
        plt.xlabel('Constituency ID', fontsize=12)
        plt.ylabel('MP-Party Difference', fontsize=12)
        plt.title('MP-Party Difference by Constituency (|error/station| > 3, sorted max to min)', 
                  fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        
        # Add horizontal line at 0
        plt.axhline(y=0, color='red', linestyle='--', linewidth=2, label='Zero difference')
        plt.legend()
        
        # Save the plot
        plot_path = data_dir / 'interest_constituency_mp_party_diff.png'
        plt.savefig(plot_path, dpi=600, bbox_inches='tight')
        print(f"Plot saved to {plot_path}")
        
        # Show the plot
        plt.show()

    dfofUninterest = df[df['mp_party_error_per_station'].abs() <= 3]
    print(f"\nConstituencies with |mp_party_error_per_station| <= 3: {len(dfofUninterest)}")
    # Save to JSON  
    output_json_path = data_dir / 'uninterest_constituency.json'
    print(f"Saving to {output_json_path}...")
    dfofUninterest.to_json(output_json_path, orient='records', force_ascii=False, indent=2)
    # Save to Excel
    output_xlsx_path = data_dir / 'uninterest_constituency.xlsx'
    print(f"Saving to {output_xlsx_path}...")
    dfofUninterest.to_excel(output_xlsx_path, index=False, sheet_name='Constituencies')

