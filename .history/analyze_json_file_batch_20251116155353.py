import os
import sys



def main():
    # Step 1: select a folder containing the data files
    data_folder = "/Users/alessiotamborini/Documents/Avicena/LeakageTests/Data/SampleData/"

    # visualize the name of the files in the folder
    data_files = sorted([file for file in os.listdir(data_folder) if file.endswith(".json")])
    print(f"Number of data files in the folder: {len(data_files)}")
    print("Data files in the folder:")
    for i, file in enumerate(data_files):
        print(f"    {i}: {file}")

    # Step 2: load the data files
    data = {}
    for file in data_files:
        with open(os.path.join(data_folder, file), 'r') as f:
            data[file] = json.load(f)
    sample_data = data[data_files[0]]
    print(f"Sample data keys:\n{list(sample_data.keys())}")

if __name__ == "__main__":
    main()