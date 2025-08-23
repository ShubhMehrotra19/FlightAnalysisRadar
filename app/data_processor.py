import pandas as pd
import numpy as np
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles data extraction, cleaning, and transformation"""
    
    def __init__(self, config, data_dir):
        self.config = config
        self.data_dir = Path(data_dir)
        
    def extract_data(self):
        """Extract raw data from source"""
        file_path = self.data_dir / self.config['data_source']
        
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        logger.info(f"Loading data from: {file_path}")
        df_raw = pd.read_excel(file_path, header=None)
        
        return df_raw
    
    def transform_data(self, df_raw):
        """Clean and transform raw data"""
        logger.info("Starting data transformation...")
        
        # Remove rows where all values are NaN
        df = df_raw.dropna(how='all')
        
        # Find header row
        header_row = self._find_header_row(df)
        columns = df.iloc[header_row].fillna('').tolist()
        
        # Clean data structure
        cleaned_df = df.iloc[header_row+1:]
        cleaned_df.columns = columns
        cleaned_df = cleaned_df.reset_index(drop=True)
        
        # Remove repeated headers
        cleaned_df = cleaned_df[cleaned_df['Flight Number'] != 'Flight Number']
        
        # Clean columns
        cleaned_df = self._clean_columns(cleaned_df)
        
        # Parse dates and times
        cleaned_df = self._parse_datetime_fields(cleaned_df)
        
        # Calculate delays
        cleaned_df = self._calculate_delays(cleaned_df)
        
        # Add derived features
        cleaned_df = self._add_derived_features(cleaned_df)
        
        # Save processed data
        output_path = self.data_dir / f"{self.config['data_source'].replace('.xlsx', '_processed.csv')}"
        cleaned_df.to_csv(output_path, index=False)
        logger.info(f"Processed data saved to: {output_path}")
        
        return cleaned_df
    
    def _find_header_row(self, df):
        """Find the row containing column headers"""
        for i in range(min(10, len(df))):
            row_values = df.iloc[i].astype(str)
            if row_values.str.contains('Flight Number', case=False, na=False).any():
                return i
        return 0
    
    def _clean_columns(self, df):
        """Clean and standardize column names"""
        # Handle duplicate column names
        cols = df.columns.tolist()
        seen = {}
        for i, col in enumerate(cols):
            if col in seen:
                seen[col] += 1
                cols[i] = f"{col}{seen[col]}" if col else f"unnamed{seen[col]}"
            else:
                seen[col] = 0
                if col == '':
                    cols[i] = f"date_col_{i}"
        df.columns = cols
        
        # Drop empty columns
        df = df.dropna(axis=1, how='all')
        
        return df
    
    def _parse_datetime_fields(self, df):
        """Parse date and time fields"""
        # Find date column
        date_col = self._find_date_column(df)
        
        if date_col:
            df['Date'] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Parse ATA to extract time
            if 'ATA' in df.columns:
                df['ATA_time'] = df['ATA'].str.extract(r'Landed\s*([0-9:]+\s*[APM]{2})', expand=False)
            
            # Convert time columns to datetime
            time_cols = ['STD', 'ATD', 'STA']
            if 'ATA_time' in df.columns:
                time_cols.append('ATA_time')
            
            for col in time_cols:
                if col in df.columns:
                    datetime_strings = df['Date'].dt.strftime('%Y-%m-%d') + ' ' + df[col].astype(str)
                    df[col + '_dt'] = pd.to_datetime(datetime_strings, errors='coerce')
        
        return df
    
    def _find_date_column(self, df):
        """Identify the date column"""
        for col in df.columns:
            sample_values = df[col].dropna().astype(str).head(10)
            if any(re.search(r'\d{1,2}-[A-Za-z]{3}-\d{2,4}', str(val)) for val in sample_values):
                return col
        
        # Fallback options
        potential_cols = [col for col in df.columns if 'date_col' in col or col == '']
        if potential_cols:
            return potential_cols[0]
        elif len(df.columns) > 2:
            return df.columns[2]
        
        return None
    
    def _calculate_delays(self, df):
        """Calculate departure and arrival delays"""
        # Calculate delays in minutes
        if 'STD_dt' in df.columns and 'ATD_dt' in df.columns:
            df['Departure Delay (min)'] = (df['ATD_dt'] - df['STD_dt']).dt.total_seconds() / 60
        
        if 'STA_dt' in df.columns and 'ATA_time_dt' in df.columns:
            df['Arrival Delay (min)'] = (df['ATA_time_dt'] - df['STA_dt']).dt.total_seconds() / 60
        
        return df
    
    def _add_derived_features(self, df):
        """Add derived features for analysis"""
        # Extract hour features
        if 'STD_dt' in df.columns:
            df['Departure Hour'] = df['STD_dt'].dt.hour
        if 'STA_dt' in df.columns:
            df['Arrival Hour'] = df['STA_dt'].dt.hour
        
        # Extract airline codes
        if 'Flight Number' in df.columns:
            df['Airline'] = df['Flight Number'].str.extract(r'([A-Z]{2,3})')
        
        # Add day of week
        if 'Date' in df.columns:
            df['Day of Week'] = df['Date'].dt.day_name()
            df['Is Weekend'] = df['Date'].dt.weekday >= 5
        
        # On-time performance flag
        delay_threshold = self.config['analysis_params']['delay_threshold']
        if 'Departure Delay (min)' in df.columns:
            df['On Time'] = df['Departure Delay (min)'] <= delay_threshold
        
        return df