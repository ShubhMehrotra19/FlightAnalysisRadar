import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Visualizer:
    """Generate visualizations and reports"""
    
    def __init__(self, reports_dir):
        self.reports_dir = Path(reports_dir)
        plt.style.use('default')  # Use default style instead of deprecated seaborn-v0_8
        
    def generate_reports(self, df, analysis_results):
        """Generate all visualization reports"""
        viz_results = {}
        
        # Static plots
        viz_results['static_plots'] = self._generate_static_plots(df)
        
        # Interactive dashboard
        viz_results['interactive_plots'] = self._generate_interactive_plots(df, analysis_results)
        
        # Summary report
        viz_results['summary_report'] = self._generate_summary_report(df, analysis_results)
        
        return viz_results
    
    def _generate_static_plots(self, df):
        """Generate static matplotlib/seaborn plots"""
        plots_generated = []
        
        # Flight distribution plot
        if 'Departure Hour' in df.columns:
            plt.figure(figsize=(12, 6))
            hourly_counts = df['Departure Hour'].value_counts().sort_index()
            plt.bar(hourly_counts.index, hourly_counts.values, alpha=0.7, color='skyblue')
            plt.title('Flight Distribution by Hour', fontsize=16, fontweight='bold')
            plt.xlabel('Hour of Day')
            plt.ylabel('Number of Flights')
            plt.grid(True, alpha=0.3)
            
            plot_path = self.reports_dir / 'flight_distribution_by_hour.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            plots_generated.append(str(plot_path))
        
        # Delay analysis plot
        if 'Departure Delay (min)' in df.columns:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Histogram
            delay_data = df['Departure Delay (min)'].dropna()
            ax1.hist(delay_data, bins=30, alpha=0.7, color='lightcoral', edgecolor='black')
            ax1.set_title('Delay Distribution')
            ax1.set_xlabel('Delay (minutes)')
            ax1.set_ylabel('Frequency')
            ax1.axvline(delay_data.mean(), color='red', linestyle='--', 
                       label=f'Mean: {delay_data.mean():.1f} min')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Box plot by day of week
            if 'Day of Week' in df.columns:
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                df_plot = df[df['Day of Week'].isin(day_order)]
                if len(df_plot) > 0:
                    sns.boxplot(data=df_plot, x='Day of Week', y='Departure Delay (min)', ax=ax2)
                    ax2.set_title('Delays by Day of Week')
                    ax2.tick_params(axis='x', rotation=45)
                    ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plot_path = self.reports_dir / 'delay_analysis.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            plots_generated.append(str(plot_path))
        
        return plots_generated
    
    def _generate_interactive_plots(self, df, analysis_results):
        """Generate interactive Plotly visualizations"""
        interactive_files = []
        
        # Multi-panel dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Hourly Operations', 'Delay Distribution', 
                          'Daily Trends', 'Airline Performance'),
            specs=[[{"secondary_y": True}, {"type": "histogram"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # Add traces for each subplot
        if 'Departure Hour' in df.columns:
            hourly_counts = df['Departure Hour'].value_counts().sort_index()
            fig.add_trace(
                go.Bar(x=hourly_counts.index, y=hourly_counts.values, 
                      name="Flights", opacity=0.7),
                row=1, col=1
            )
        
        if 'Departure Delay (min)' in df.columns:
            fig.add_trace(
                go.Histogram(x=df['Departure Delay (min)'].dropna(), 
                           name="Delays", nbinsx=30),
                row=1, col=2
            )
        
        if 'Date' in df.columns:
            daily_counts = df.groupby(df['Date'].dt.date).size()
            fig.add_trace(
                go.Scatter(x=daily_counts.index, y=daily_counts.values,
                          mode='lines+markers', name="Daily Flights"),
                row=2, col=1
            )
        
        if 'Airline' in df.columns:
            airline_counts = df['Airline'].value_counts().head(8)
            fig.add_trace(
                go.Bar(x=airline_counts.values, y=airline_counts.index,
                      orientation='h', name="Airlines"),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            title_text="Flight Operations Interactive Dashboard",
            title_x=0.5,
            showlegend=False
        )
        
        # Save interactive plot
        interactive_path = self.reports_dir / 'interactive_dashboard.html'
        fig.write_html(str(interactive_path))
        interactive_files.append(str(interactive_path))
        
        return interactive_files
    
    def _generate_summary_report(self, df, analysis_results):
        """Generate comprehensive summary report"""
        report_content = f"""# Flight Operations Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- **Total Flights Analyzed**: {analysis_results['basic_stats']['total_flights']:,}
- **Analysis Period**: {analysis_results['basic_stats']['date_range']['start']} to {analysis_results['basic_stats']['date_range']['end']}
- **Average Daily Operations**: {analysis_results['basic_stats']['avg_daily_flights']:.1f} flights

## Key Performance Indicators
"""
        
        if 'efficiency_metrics' in analysis_results:
            metrics = analysis_results['efficiency_metrics']
            if 'on_time_performance' in metrics:
                report_content += f"- **On-Time Performance**: {metrics['on_time_performance']*100:.1f}%\n"
            if 'severe_delay_rate' in metrics:
                report_content += f"- **Severe Delay Rate**: {metrics['severe_delay_rate']*100:.1f}%\n"
        
        if 'delay_analysis' in analysis_results:
            delay_info = analysis_results['delay_analysis']
            if 'Departure Delay (min)' in delay_info:
                dep_delay = delay_info['Departure Delay (min)']
                report_content += f"- **Average Departure Delay**: {dep_delay['mean']:.1f} minutes\n"
                report_content += f"- **95th Percentile Delay**: {dep_delay['percentiles']['95th']:.1f} minutes\n"
        
        report_content += """

## Operational Insights
"""
        
        if 'peak_analysis' in analysis_results:
            peak_info = analysis_results['peak_analysis']
            if 'busiest_hour' in peak_info:
                report_content += f"- **Busiest Operating Hour**: {peak_info['busiest_hour']}:00\n"
            if 'most_congested_hour' in peak_info:
                report_content += f"- **Most Congested Hour**: {peak_info['most_congested_hour']}:00\n"
        
        if 'cascade_analysis' in analysis_results:
            cascade_info = analysis_results['cascade_analysis']
            if 'affected_flights' in cascade_info:
                report_content += f"- **Flights Affected by Cascading Delays**: {cascade_info['affected_flights']}\n"
            if 'avg_cascade_impact' in cascade_info:
                report_content += f"- **Average Cascade Impact**: {cascade_info['avg_cascade_impact']:.1f} minutes\n"
        
        # Add simulation results
        if 'simulation' in analysis_results:
            sim_info = analysis_results['simulation']['delay_reduction_scenario']
            report_content += f"""

## Improvement Scenarios
- **Potential Delay Reduction**: {sim_info['improvement']:.1f} minutes ({sim_info['percent_improvement']:.1f}% improvement)
- **Target Average Delay**: {sim_info['simulated_avg_delay']:.1f} minutes
"""
        
        # Save report
        report_path = self.reports_dir / 'flight_analysis_report.md'
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return str(report_path)