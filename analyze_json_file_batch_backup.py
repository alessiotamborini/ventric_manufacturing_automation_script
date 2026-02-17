import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib
matplotlib.use("Agg")
plt.ioff()
import matplotlib.style as mplstyle
mplstyle.use('fast')


# ============================================================================
# DATA LOADING AND FOLDER UTILITIES
# ============================================================================

def _select_data_folder():
    """Open a dialog to select the folder containing JSON files."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    folder_path = filedialog.askdirectory(
        title="Select folder containing JSON files",
        initialdir=os.path.expanduser("~")
    )
    
    root.destroy()
    return folder_path


def _load_json_files(data_folder):
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
    
    # Load all JSON files
    data = {}
    for file in tqdm(data_files, total=len(data_files), desc="Loading JSON files"):
        try:
            with open(os.path.join(data_folder, file), 'r') as f:
                data[file] = json.load(f)
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    return data, data_files


def _create_results_folder(data_folder):
    """Create a results folder and visualizations subfolder within the data folder."""
    results_folder = os.path.join(data_folder, "analysis_results")
    visualizations_folder = os.path.join(results_folder, "visualizations")
    os.makedirs(results_folder, exist_ok=True)
    os.makedirs(visualizations_folder, exist_ok=True)
    return results_folder, visualizations_folder


# ============================================================================
# SIGNAL ANALYSIS FUNCTIONS
# ============================================================================

def _extract_cuff_data(sample_data):
    """Extract cuff data from a sample JSON file."""
    tester_info = sample_data['tester_info']
    cuff_data = tester_info['cuff_data']
    cuff_values = np.array(cuff_data['cuff_values'])
    time_values = np.array(cuff_data['time'])
    return cuff_values, time_values


def _process_ssbp_hold_signal(sample_data, cuff_values):
    """Process the sSBP hold signal to extract the relevant portion."""
    ssbp_hold = sample_data['hold_ssbp_cuff']
    length = len(ssbp_hold)
    ssbp_hold_data = cuff_values[-length:]

    # Compute last drop to cutoff signal
    gap = len(ssbp_hold_data) - np.argmax(np.abs(np.diff(ssbp_hold_data)))
    ssbp_hold_data = cuff_values[-(length+gap):-gap]
    
    return ssbp_hold_data


def _analyze_single_file(sample_data):
    """Analyze a single JSON file and return metrics."""
    # Extract cuff data
    cuff_values, time_values = _extract_cuff_data(sample_data)
    
    # Process sSBP hold signal
    ssbp_hold_data = _process_ssbp_hold_signal(sample_data, cuff_values)

    # Cutoff the signal after the drop from the max value ~95% volts
    max_value = np.max(ssbp_hold_data)
    threshold = 0.95 * max_value
    cutoff_index = np.where(ssbp_hold_data > threshold)[0][-1] + 1
    ssbp_hold_data = ssbp_hold_data[cutoff_index:]

    # Look only at the signal that has settled (last 10000 samples)
    if len(ssbp_hold_data) > 10000:
        settled_signal = ssbp_hold_data[-10000:]
    else:
        settled_signal = ssbp_hold_data

    # Determine if the signals drop to within the boundaries
    thres_7000 = np.any(settled_signal < 7000)
    thres_9000 = np.any(settled_signal < 9000)
    cond = thres_7000 and thres_9000

    return {
        'max_value': max_value,
        'min_settled_value': np.min(settled_signal),
        'mean_settled_value': np.mean(settled_signal),
        'std_settled_value': np.std(settled_signal),
        'thres_7000': thres_7000,
        'thres_9000': thres_9000,
        'cond': cond
    }


def analyze_all_files(data, data_files):
    """Analyze all JSON files and return results as a DataFrame."""
    results = []
    
    for file_name, sample_data in tqdm(data.items(), total=len(data), desc="Analyzing files"):
        try:
            metrics = _analyze_single_file(sample_data)
            result = {
                'file_name': file_name,
                **metrics
            }
            results.append(result)
            
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            result = {
                'file_name': file_name,
                'thres_7000': False,
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


# ============================================================================
# PLOTTING AND VISUALIZATION FUNCTIONS
# ============================================================================

def _plot_sample_visualization(sample_data, file_name, visualizations_folder):
    """Create visualization for a sample file and save to visualizations folder."""
    # Extract and process data
    cuff_values, time_values = _extract_cuff_data(sample_data)
    ssbp_hold_data = _process_ssbp_hold_signal(sample_data, cuff_values)

    # Generate visualization
    fig, ax = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [2, 1]}, sharey=True)
    
    # Plot full signal
    ax[0].plot(time_values, cuff_values)
    ax[0].grid(axis='y')
    ax[0].set_title(f'Full Cuff Signal - {file_name}')
    ax[0].set_xlabel('Time (n)')
    ax[0].set_ylabel('Signal Amplitude')
    
    # Plot sSBP hold signal
    ax[1].plot(ssbp_hold_data, label='Signal')
    ax[1].axhline(np.mean(ssbp_hold_data[-10000:]), color='b', linestyle='-', label='Mean of Settled Signal')
    ax[1].axhline(y=7000, color='r', linestyle='--', label='7000 line')
    ax[1].axhline(y=9000, color='g', linestyle='--', label='9000 line')
    ax[1].grid(axis='y')
    ax[1].set_title('sSBP Hold Signal')
    ax[1].set_xlabel('Time (n)')
    ax[1].legend()
    ax[1].set_yticks(np.arange(0, 17000, 2000))
    
    plt.tight_layout()
    
    # Save the plot
    plot_filename = f"{os.path.splitext(file_name)[0]}.png"
    plot_path = os.path.join(visualizations_folder, plot_filename)
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close(fig)


def create_sample_visualizations(data, data_files, visualizations_folder):
    """Create sample visualizations for all JSON files."""
    print(f"\nCreating sample visualizations for all {len(data_files)} files...")
    
    # Create the sample visualizations save folder
    sample_visualizations_folder = os.path.join(visualizations_folder, "signal_visualizations")
    os.makedirs(sample_visualizations_folder, exist_ok=True)
    
    for file_name in tqdm(data_files, desc="Creating sample visualizations"):
        try:
            sample_data = data[file_name]
            _plot_sample_visualization(sample_data, file_name, sample_visualizations_folder)
        except Exception as e:
            print(f"Error creating visualization for {file_name}: {e}")
    
    print("Sample visualizations completed!")


def create_summary_dashboard(results_df, visualizations_folder):
    """Create and save a summary dashboard with analysis statistics."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Threshold compliance
    axes[0, 0].bar(['7000 Threshold', '9000 Threshold', 'Both Conditions'], 
                   [results_df['thres_7000'].sum(), results_df['thres_9000'].sum(), results_df['cond'].sum()])
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
    axes[1, 0].axvline(x=7000, color='r', linestyle='--', label='7000 threshold')
    axes[1, 0].axvline(x=9000, color='g', linestyle='--', label='9000 threshold')
    axes[1, 0].legend()
    
    # Mean settled values distribution
    axes[1, 1].hist(results_df['mean_settled_value'].dropna(), bins=20, alpha=0.7)
    axes[1, 1].set_title('Distribution of Mean Settled Values')
    axes[1, 1].set_xlabel('Mean Settled Value')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].axvline(x=7000, color='r', linestyle='--', label='7000 threshold')
    axes[1, 1].axvline(x=9000, color='g', linestyle='--', label='9000 threshold')
    axes[1, 1].legend()
    text = f'Total Files: {len(results_df)}\nMean: {results_df["mean_settled_value"].mean():.2f}\nStd: {results_df["mean_settled_value"].std():.2f}\nMedian: {results_df["mean_settled_value"].median():.2f}\nMax: {results_df["mean_settled_value"].max():.2f}\nMin: {results_df["mean_settled_value"].min():.2f}'
    axes[1, 1].text(0.95, 0.95, text, transform=axes[1, 1].transAxes,verticalalignment='top', horizontalalignment='right')
    
    plt.tight_layout()
    
    # Save summary dashboard
    summary_plot_path = os.path.join(visualizations_folder, "summary_dashboard.png")
    plt.savefig(summary_plot_path, bbox_inches='tight')
    plt.close(fig)  # Close the figure to free memory
    print(f"Summary dashboard saved to: {summary_plot_path}")
    
    print(f"\nAnalysis complete!")
    print(f"Results saved to: {results_folder}")
    print(f"Visualizations saved to: {visualizations_folder}")


if __name__ == "__main__":
    main()

# ============================================================================
# RESULTS HANDLING
# ============================================================================

def save_results(results_df, results_folder):
    """Save results to CSV file."""
    csv_file = os.path.join(results_folder, "analysis_results.csv")
    results_df.to_csv(csv_file, index=False)
    print(f"Results saved to CSV: {csv_file}")


def print_summary_statistics(results_df):
    """Print summary statistics from the analysis."""
    print(f"\nSummary Statistics:")
    print(f"Total files analyzed: {len(results_df)}")
    print(f"Files meeting 7000 threshold: {results_df['thres_7000'].sum()}")
    print(f"Files meeting 9000 threshold: {results_df['thres_9000'].sum()}")
    print(f"Files meeting both conditions: {results_df['cond'].sum()}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to run the batch analysis."""
    print("JSON Batch Analysis Tool")
    print("=" * 40)
    
    # Step 1: Select folder containing JSON files
    data_folder = _select_data_folder()
    if not data_folder:
        print("No folder selected. Exiting.")
        return
    
    print(f"Selected folder: {data_folder}")
    
    # Step 2: Load JSON files
    data, data_files = _load_json_files(data_folder)
    if data is None:
        return
    
    # Step 3: Create results and visualizations folders
    results_folder, visualizations_folder = _create_results_folder(data_folder)
    print(f"Results will be saved to: {results_folder}")
    print(f"Visualizations will be saved to: {visualizations_folder}")
    
    # Step 4: Create sample visualizations for all files
    create_sample_visualizations(data, data_files, visualizations_folder)
    
    # Step 5: Analyze all files
    print("\nAnalyzing all files...")
    results_df = analyze_all_files(data, data_files)
    
    # Step 6: Display and save results
    print("\nAnalysis Results:")
    print("=" * 50)
    print(results_df)
    
    # Print summary statistics
    print_summary_statistics(results_df)
    
    # Save results to CSV
    save_results(results_df, results_folder)
    
    # Create and save summary dashboard
    create_summary_dashboard(results_df, visualizations_folder)
    
    print(f"\nAnalysis complete!")
    print(f"Results saved to: {results_folder}")
    print(f"Visualizations saved to: {visualizations_folder}")
