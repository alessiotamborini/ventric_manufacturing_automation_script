import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Note: openpyxl is required for Excel file writing - install with: pip install openpyxl


def select_data_folder():
    """Open a dialog to select the folder containing JSON files."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    folder_path = filedialog.askdirectory(
        title="Select folder containing JSON files",
        initialdir=os.path.expanduser("~")
    )
    
    root.destroy()
    return folder_path


def load_json_files(data_folder):
    """Load all JSON files from the selected folder."""
    if not data_folder:
        print("No folder selected. Exiting.")
        return None, None
    
    # Get all JSON files in the folder
    data_files = sorted([file for file in os.listdir(data_folder) if file.endswith(".json")])
    
    if not data_files:
        messagebox.showerror("Error", "No JSON files found in the selected folder.")
        return None, None
    
    print(f"Number of data files in the folder: {len(data_files)}")
    print("Data files in the folder:")
    for i, file in enumerate(data_files):
        print(f"    {i}: {file}")
    
    # Load all JSON files
    data = {}
    for file in data_files:
        try:
            with open(os.path.join(data_folder, file), 'r') as f:
                data[file] = json.load(f)
            print(f"Loaded: {file}")
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    return data, data_files


def create_results_folder(data_folder):
    """Create a results folder within the data folder."""
    results_folder = os.path.join(data_folder, "analysis_results")
    os.makedirs(results_folder, exist_ok=True)
    return results_folder


def process_sample_visualization(sample_data, file_name, results_folder):
    """Create visualization for a sample file and save to results folder."""
    # Extract cuff data
    tester_info = sample_data['tester_info']
    cuff_data = tester_info['cuff_data']
    cuff_values = np.array(cuff_data['cuff_values'])
    time_values = np.array(cuff_data['time'])

    # Process sSBP hold data
    ssbp_hold = sample_data['hold_ssbp_cuff']
    length = len(ssbp_hold)
    ssbp_hold_data = cuff_values[-length:]

    # Compute last drop
    gap = len(ssbp_hold_data) - np.argmax(np.abs(np.diff(ssbp_hold_data)))
    ssbp_hold_data = cuff_values[-(length+gap):-gap]

    # Generate visualization
    fig, ax = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [2, 1]}, sharey=True)
    ax[0].plot(time_values, cuff_values)
    ax[0].grid(axis='y')
    ax[0].set_title(f'Full Cuff Signal - {file_name}')
    ax[0].set_xlabel('Time (n)')
    ax[0].set_ylabel('Signal Amplitude')
    
    ax[1].plot(ssbp_hold_data, label='Signal')
    ax[1].axhline(y=8000, color='r', linestyle='--', label='8000 line')
    ax[1].axhline(y=9000, color='g', linestyle='--', label='9000 line')
    ax[1].grid(axis='y')
    ax[1].set_title('sSBP Hold Signal')
    ax[1].set_xlabel('Time (n)')
    ax[1].legend()
    
    plt.tight_layout()
    
    # Save the plot
    plot_filename = f"sample_visualization_{os.path.splitext(file_name)[0]}.png"
    plot_path = os.path.join(results_folder, plot_filename)
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close the figure to free memory
    print(f"Sample visualization saved to: {plot_path}")


def analyze_all_files(data, data_files, results_folder):
    """Analyze all JSON files and return results."""
    results = []
    
    for i, (key, item) in enumerate(data.items()):
        try:
            # Extract cuff data
            tester_info = item['tester_info']
            cuff_data = tester_info['cuff_data']
            cuff_values = np.array(cuff_data['cuff_values'])
            time_values = np.array(cuff_data['time'])

            # Process sSBP hold data
            ssbp_hold = item['hold_ssbp_cuff']
            length = len(ssbp_hold)
            ssbp_hold_data = cuff_values[-length:]

            # Compute last drop to cutoff signal
            gap = len(ssbp_hold_data) - np.argmax(np.abs(np.diff(ssbp_hold_data)))
            ssbp_hold_data = cuff_values[-(length+gap):-gap]

            # Cutoff the signal after the drop from the max value ~95% volts
            max_value = np.max(ssbp_hold_data)
            threshold = 0.95 * max_value
            cutoff_index = np.where(ssbp_hold_data > threshold)[0][-1] + 1
            ssbp_hold_data = ssbp_hold_data[cutoff_index:]

            # Look only at the signal that has settled (last 10000 samples)
            if len(ssbp_hold_data) > 10000:
                ind = len(ssbp_hold_data) - 10000
                arr = ssbp_hold_data[ind:]
            else:
                arr = ssbp_hold_data
                ind = 0

            # Determine if the signals drop to within the boundaries
            thres_8000 = np.any(arr < 8000)
            thres_9000 = np.any(arr < 9000)
            cond = thres_8000 and thres_9000

            # Generate detailed plot for the first file as example
            if i == 0:
                fig, ax = plt.subplots(1, 2, figsize=(12, 6))
                ax[0].plot(ssbp_hold_data, label='Signal')
                ax[0].axvline(x=ind, color='b', linestyle='--', label='Settled Signal Start')
                ax[1].plot(arr, label='Settled Signal')
                ax[1].axhline(y=8000, color='r', linestyle='--', label='8000 line')
                ax[1].axhline(y=9000, color='g', linestyle='--', label='9000 line')
                ax[0].grid(axis='y')
                ax[1].grid(axis='y')
                ax[0].set_title(f'sSBP Hold Signal - {key}')
                ax[0].set_xlabel('Time (n)')
                ax[1].set_title('Settled sSBP Hold Signal')
                ax[1].set_xlabel('Time (n)')
                ax[0].legend()
                ax[1].legend()
                plt.tight_layout()
                
                # Save the detailed plot
                detailed_plot_filename = f"detailed_analysis_{os.path.splitext(key)[0]}.png"
                detailed_plot_path = os.path.join(results_folder, detailed_plot_filename)
                plt.savefig(detailed_plot_path, dpi=300, bbox_inches='tight')
                plt.close()  # Close the figure to free memory
                print(f"Detailed analysis plot saved to: {detailed_plot_path}")

            # Store results
            result = {
                'file_name': key,
                'thres_8000': thres_8000,
                'thres_9000': thres_9000,
                'cond': cond,
                'max_value': max_value,
                'min_settled_value': np.min(arr),
                'mean_settled_value': np.mean(arr),
                'std_settled_value': np.std(arr)
            }
            results.append(result)
            
        except Exception as e:
            print(f"Error processing {key}: {e}")
            result = {
                'file_name': key,
                'thres_8000': False,
                'thres_9000': False,
                'cond': False,
                'max_value': np.nan,
                'min_settled_value': np.nan,
                'mean_settled_value': np.nan,
                'std_settled_value': np.nan,
                'error': str(e)
            }
            results.append(result)
    
    return pd.DataFrame(results)


def save_results(results_df, data_folder):
    """Save results to CSV file."""
    output_file = os.path.join(data_folder, "analysis_results.csv")
    results_df.to_csv(output_file, index=False)
    print(f"Results saved to: {output_file}")


def main():
    """Main function to run the batch analysis."""
    print("JSON Batch Analysis Tool")
    print("=" * 40)
    
    # Step 1: Select folder containing JSON files
    data_folder = select_data_folder()
    if not data_folder:
        print("No folder selected. Exiting.")
        return
    
    print(f"Selected folder: {data_folder}")
    
    # Step 2: Load JSON files
    data, data_files = load_json_files(data_folder)
    if data is None:
        return
    
    # Step 3: Show sample visualization for the first file
    if data_files:
        sample_file = data_files[0]
        sample_data = data[sample_file]
        print(f"\nSample data keys from {sample_file}:")
        print(list(sample_data.keys()))
        
        # Show sample visualization
        process_sample_visualization(sample_data, sample_file)
    
    # Step 4: Analyze all files
    print("\nAnalyzing all files...")
    results_df = analyze_all_files(data, data_files)
    
    # Step 5: Display and save results
    print("\nAnalysis Results:")
    print("=" * 50)
    print(results_df)
    
    # Show summary statistics
    print(f"\nSummary Statistics:")
    print(f"Total files analyzed: {len(results_df)}")
    print(f"Files meeting 8000 threshold: {results_df['thres_8000'].sum()}")
    print(f"Files meeting 9000 threshold: {results_df['thres_9000'].sum()}")
    print(f"Files meeting both conditions: {results_df['cond'].sum()}")
    
    # Save results
    save_results(results_df, data_folder)
    
    # Create summary visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Threshold compliance
    axes[0, 0].bar(['8000 Threshold', '9000 Threshold', 'Both Conditions'], 
                   [results_df['thres_8000'].sum(), results_df['thres_9000'].sum(), results_df['cond'].sum()])
    axes[0, 0].set_title('Threshold Compliance')
    axes[0, 0].set_ylabel('Number of Files')
    
    # Max values distribution
    axes[0, 1].hist(results_df['max_value'].dropna(), bins=20, alpha=0.7)
    axes[0, 1].set_title('Distribution of Max Values')
    axes[0, 1].set_xlabel('Max Value')
    axes[0, 1].set_ylabel('Frequency')
    
    # Min settled values distribution
    axes[1, 0].hist(results_df['min_settled_value'].dropna(), bins=20, alpha=0.7)
    axes[1, 0].set_title('Distribution of Min Settled Values')
    axes[1, 0].set_xlabel('Min Settled Value')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].axvline(x=8000, color='r', linestyle='--', label='8000 threshold')
    axes[1, 0].axvline(x=9000, color='g', linestyle='--', label='9000 threshold')
    axes[1, 0].legend()
    
    # Mean settled values distribution
    axes[1, 1].hist(results_df['mean_settled_value'].dropna(), bins=20, alpha=0.7)
    axes[1, 1].set_title('Distribution of Mean Settled Values')
    axes[1, 1].set_xlabel('Mean Settled Value')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].axvline(x=8000, color='r', linestyle='--', label='8000 threshold')
    axes[1, 1].axvline(x=9000, color='g', linestyle='--', label='9000 threshold')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.show()
    
    print("Analysis complete!")


if __name__ == "__main__":
    main()