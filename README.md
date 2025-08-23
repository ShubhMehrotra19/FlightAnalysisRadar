# Flight Data Analysis Pipeline

A comprehensive flight operations analysis system for airport data processing and visualization.

## Features
- ✈️ Complete flight data processing pipeline
- 📊 Advanced delay and operational analysis
- 📈 Interactive visualizations and dashboards
- 🔄 What-if scenario simulations
- 🎯 Cascading delay impact modeling
- 📋 Automated report generation

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Place your flight data file in the data/ directory**
   - Your Excel file should be named: `429e6e3f-281d-4e4c-b00a-92fb020cb2fcFlight_Data.xlsx`
   - Or update the filename in `config.json`

3. **Run the complete pipeline:**
```bash
python main.py
```

4. **Or run specific steps:**
```bash
python main.py --steps extract transform analyze
```

5. **Launch interactive dashboard:**
```bash
python main.py --steps dashboard
```

## Project Structure

```
FlightRadarAnalytics/
├── app/
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── flight_data_pipeline.py    # Main orchestrator
│   ├── __init__.py
│   ├── data_processor.py              # ETL operations
│   ├── analyzer.py                    # Core analysis
│   ├── visualizer.py                  # Report generation
│   └── dashboard_generator.py         # Interactive dashboard
├── data/                              # Your Excel files go here
├── notebooks/                         # Jupyter notebooks
├── reports/                           # Generated visualizations
├── config.py                         # Configuration management
├── config.json                       # Configuration file
├── main.py                           # CLI entry point
├── requirements.txt                  # Dependencies
└── README.md                         # This file
```

## Dataset Placement

**Important:** Place your Excel dataset file in the `data/` folder with the exact filename:
- `429e6e3f-281d-4e4c-b00a-92fb020cb2fcFlight_Data.xlsx`

Or you can:
1. Rename your file to match the above name, or
2. Update the `data_source` field in `config.json` to match your filename

## Configuration

Edit `config.json` to customize analysis parameters and data sources:

```json
{
    "data_source": "your_flight_data.xlsx",
    "analysis_params": {
        "delay_threshold": 15,
        "cascade_factor": 0.4,
        "simulation_delay_reduction": 5,
        "peak_hour_shift": 1
    },
    "output_formats": ["csv", "json", "html"],
    "dashboard_port": 8050
}
```

## Output

- **Processed data:** `data/` folder
- **Visualizations:** `reports/` folder
- **Interactive dashboard:** Browser-based at http://localhost:8050

## Usage Examples

### Run complete analysis:
```bash
python main.py
```

### Run only data processing:
```bash
python main.py --steps extract transform
```

### Run analysis with custom data file:
```bash
python main.py --data-file "my_flight_data.xlsx"
```

### Custom configuration:
```bash
python main.py --config "my_config.json"
```

## Pipeline Steps

1. **Extract**: Load raw data from Excel file
2. **Transform**: Clean and process the data
3. **Analyze**: Perform delay analysis, peak time analysis, etc.
4. **Visualize**: Generate static plots and reports
5. **Dashboard**: Create interactive web dashboard

## Analysis Features

- Flight distribution by hour
- Delay pattern analysis
- Airline performance comparison
- Peak time identification
- Cascading delay impact modeling
- What-if scenario simulations
- On-time performance metrics

## Troubleshooting

1. **File not found error**: Ensure your Excel file is in the `data/` folder with correct filename
2. **Import errors**: Run `pip install -r requirements.txt`
3. **Dashboard not loading**: Check if port 8050 is available, or change port in config
4. **Memory issues**: Large datasets may require more RAM

## Requirements

- Python 3.7+
- pandas, numpy, matplotlib, seaborn, plotly, dash
- Excel file with flight data

## License

This project is for educational and analysis purposes.