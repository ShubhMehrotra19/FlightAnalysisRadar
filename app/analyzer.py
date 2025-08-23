import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FlightAnalyzer:
    """Core analysis engine"""
    
    def __init__(self, config):
        self.config = config
        self.analysis_params = config['analysis_params']
    
    def run_analysis(self, df):
        """Execute complete analysis suite"""
        results = {}
        
        # Basic statistics
        results['basic_stats'] = self._calculate_basic_stats(df)
        
        # Peak time analysis
        results['peak_analysis'] = self._analyze_peak_times(df)
        
        # Delay analysis
        results['delay_analysis'] = self._analyze_delays(df)
        
        # Operational efficiency
        results['efficiency_metrics'] = self._calculate_efficiency_metrics(df)
        
        # Simulation results
        results['simulation'] = self._run_simulations(df)
        
        # Cascading impact
        results['cascade_analysis'] = self._analyze_cascading_impact(df)
        
        return results
    
    def _calculate_basic_stats(self, df):
        """Calculate basic operational statistics"""
        stats = {
            'total_flights': len(df),
            'unique_airlines': df['Airline'].nunique() if 'Airline' in df.columns else 0,
            'date_range': {
                'start': df['Date'].min().isoformat() if 'Date' in df.columns and not df['Date'].isna().all() else None,
                'end': df['Date'].max().isoformat() if 'Date' in df.columns and not df['Date'].isna().all() else None
            },
            'avg_daily_flights': len(df) / df['Date'].nunique() if 'Date' in df.columns and not df['Date'].isna().all() else 0
        }
        return stats
    
    def _analyze_peak_times(self, df):
        """Analyze peak operational times"""
        if 'Departure Hour' not in df.columns:
            return {}
        
        hourly_stats = df.groupby('Departure Hour').agg({
            'Flight Number': 'count',
            'Departure Delay (min)': ['mean', 'std']
        }).round(2)
        
        hourly_stats.columns = ['Flight Count', 'Avg Delay', 'Delay Std']
        
        # Calculate congestion index
        hourly_stats['Congestion Index'] = (
            hourly_stats['Flight Count'] * hourly_stats['Avg Delay'].fillna(0)
        )
        
        peak_hours = hourly_stats.nlargest(5, 'Flight Count')
        
        return {
            'hourly_stats': hourly_stats.to_dict(),
            'peak_hours': peak_hours.to_dict(),
            'busiest_hour': hourly_stats.idxmax()['Flight Count'],
            'most_congested_hour': hourly_stats.idxmax()['Congestion Index']
        }
    
    def _analyze_delays(self, df):
        """Comprehensive delay analysis"""
        delay_cols = [col for col in df.columns if 'Delay' in col and 'min' in col]
        
        if not delay_cols:
            return {}
        
        analysis = {}
        
        for col in delay_cols:
            delay_data = df[col].dropna()
            if len(delay_data) > 0:
                analysis[col] = {
                    'mean': float(delay_data.mean()),
                    'median': float(delay_data.median()),
                    'std': float(delay_data.std()),
                    'percentiles': {
                        '25th': float(delay_data.quantile(0.25)),
                        '75th': float(delay_data.quantile(0.75)),
                        '95th': float(delay_data.quantile(0.95))
                    },
                    'on_time_rate': float((delay_data <= self.analysis_params['delay_threshold']).mean())
                }
        
        # Day of week analysis
        if 'Day of Week' in df.columns and delay_cols:
            daily_delays = df.groupby('Day of Week')[delay_cols[0]].mean().to_dict()
            analysis['daily_patterns'] = daily_delays
        
        return analysis
    
    def _calculate_efficiency_metrics(self, df):
        """Calculate operational efficiency metrics"""
        metrics = {}
        
        if 'On Time' in df.columns:
            metrics['on_time_performance'] = float(df['On Time'].mean())
        
        if 'Departure Delay (min)' in df.columns:
            severe_delays = (df['Departure Delay (min)'] > 30).sum()
            metrics['severe_delay_rate'] = float(severe_delays / len(df))
        
        if 'Airline' in df.columns and 'On Time' in df.columns:
            airline_performance = df.groupby('Airline')['On Time'].mean().to_dict()
            metrics['airline_performance'] = airline_performance
        
        return metrics
    
    def _run_simulations(self, df):
        """Run what-if simulations"""
        if 'Departure Delay (min)' not in df.columns:
            return {}
        
        # Delay reduction simulation
        reduction = self.analysis_params['simulation_delay_reduction']
        simulated_delays = df['Departure Delay (min)'] - reduction
        simulated_delays = simulated_delays.clip(lower=-15)
        
        current_avg = df['Departure Delay (min)'].mean()
        simulated_avg = simulated_delays.mean()
        improvement = current_avg - simulated_avg
        
        return {
            'delay_reduction_scenario': {
                'reduction_minutes': reduction,
                'current_avg_delay': float(current_avg),
                'simulated_avg_delay': float(simulated_avg),
                'improvement': float(improvement),
                'percent_improvement': float((improvement / current_avg) * 100) if current_avg != 0 else 0
            }
        }
    
    def _analyze_cascading_impact(self, df):
        """Analyze cascading delay impacts"""
        if 'Airline' not in df.columns or 'Departure Delay (min)' not in df.columns:
            return {}
        
        cascade_impacts = []
        cascade_factor = self.analysis_params['cascade_factor']
        
        for airline in df['Airline'].dropna().unique():
            airline_flights = df[df['Airline'] == airline].copy()
            if 'STD_dt' in airline_flights.columns and len(airline_flights) > 1:
                airline_flights = airline_flights.sort_values('STD_dt')
                
                for i in range(1, len(airline_flights)):
                    prev_delay = airline_flights.iloc[i-1]['Departure Delay (min)']
                    if pd.notna(prev_delay) and prev_delay > 15:
                        cascade_delay = prev_delay * cascade_factor
                        cascade_impacts.append({
                            'flight': airline_flights.iloc[i]['Flight Number'],
                            'cascade_delay': cascade_delay,
                            'original_delay': airline_flights.iloc[i]['Departure Delay (min)']
                        })
        
        return {
            'affected_flights': len(cascade_impacts),
            'avg_cascade_impact': np.mean([x['cascade_delay'] for x in cascade_impacts]) if cascade_impacts else 0,
            'total_cascade_minutes': sum([x['cascade_delay'] for x in cascade_impacts])
        }