# JSON Analysis Tool - Windows Executable

This tool analyzes JSON files from manufacturing tests and generates visualizations and summary reports.

## For End Users (Windows)

### What you receive:
- `JSON_Analysis_Tool.exe` - The main application

### How to use:
1. **Double-click** `JSON_Analysis_Tool.exe` to start the program
2. A dialog box will open asking you to **select a folder**
3. Navigate to and select the folder containing your `.json` files
4. Click **"Select Folder"**
5. The program will automatically:
   - Process all JSON files in the folder
   - Create an `analysis_results` folder
   - Generate a CSV file with results
   - Create visualization plots in the `visualizations` subfolder

### Output:
After processing, you'll find:
```
your_data_folder/
├── your_json_files.json (your original files)
├── analysis_results/
│   ├── analysis_results.csv          # Main results spreadsheet
│   └── visualizations/               # All charts and graphs
│       ├── sample_visualization_*.png
│       ├── detailed_analysis_*.png
│       └── summary_dashboard.png
```

### Requirements:
- Windows 7 or later
- No Python installation required
- No additional software needed

### Troubleshooting:
- If the program doesn't start, try running it as Administrator
- Make sure you have read/write permissions to the folder containing your JSON files
- The program creates files in the same location as your data, so ensure there's enough disk space

---

## For Developers

### Building the executable:

#### Option 1: Automatic build (Recommended)
```bash
python build_executable.py
```

#### Option 2: Manual build
```bash
# Install requirements
pip install -r requirements.txt

# Build executable
pyinstaller --onefile --windowed --name "JSON_Analysis_Tool" analyze_json_file_batch.py
```

#### Option 3: Windows batch file
```cmd
build_executable.bat
```

### Distribution:
1. Copy the entire `dist` folder to target machine
2. The executable is completely portable - no installation needed

### Dependencies:
- Python 3.7+
- numpy, pandas, matplotlib
- tkinter (usually included with Python)
- pyinstaller (for building)

### Build output:
- `dist/JSON_Analysis_Tool.exe` - Main executable
- `build/` - Temporary build files (can be deleted)