# ==========================================
# ENHANCED DASHBOARD MODULE WITH NLP
# ==========================================
# File: FlightRadarAnalytics/app/dashboard_generator.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import re
from pathlib import Path
import json
from datetime import datetime

class DashboardGenerator:
    """Generate interactive web dashboard with NLP query capabilities"""
    
    def __init__(self, config):
        self.config = config
        self.df = None
        self.analysis_results = None
        
    def create_dashboard(self, df, analysis_results):
        """Create standalone HTML dashboard with NLP functionality"""
        self.df = df
        self.analysis_results = analysis_results
        
        # Generate the complete dashboard HTML
        dashboard_html = self._generate_dashboard_html()
        
        # Save dashboard to reports directory
        dashboard_path = Path(self.config.get('reports_dir', 'reports')) / 'flight_dashboard.html'
        dashboard_path.parent.mkdir(exist_ok=True)
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        print(f"🖥️  Interactive dashboard saved to: {dashboard_path}")
        print(f"📂 Open this file in your web browser to view the dashboard")
        
        return str(dashboard_path)
    
    def _generate_dashboard_html(self):
        """Generate complete HTML dashboard with embedded JavaScript and NLP"""
        
        # Create all visualizations
        charts_html = self._create_all_charts()
        
        # Generate data for NLP queries
        data_json = self._prepare_data_for_nlp()
        
        # Create the complete HTML
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✈️ Flight Operations Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(45deg, #1e3c72, #2a5298);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
            letter-spacing: 2px;
        }}
        
        .nlp-section {{
            background: #f8f9fa;
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .query-input {{
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
            box-sizing: border-box;
        }}
        
        .query-input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .query-btn {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
            transition: transform 0.2s;
        }}
        
        .query-btn:hover {{
            transform: translateY(-2px);
        }}
        
        .query-result {{
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            min-height: 50px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 25px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .charts-container {{
            padding: 25px;
        }}
        
        .chart {{
            margin-bottom: 30px;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .sample-queries {{
            margin-top: 15px;
        }}
        
        .sample-query {{
            display: inline-block;
            background: #e9ecef;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }}
        
        .sample-query:hover {{
            background: #667eea;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>✈️ Flight Operations Dashboard</h1>
            <p>Interactive Analysis with Natural Language Queries</p>
        </div>
        
        <!-- NLP Query Section -->
        <div class="nlp-section">
            <h2>🤖 Ask Questions About Your Flight Data</h2>
            <input type="text" id="queryInput" class="query-input" 
                   placeholder="Ask questions like: 'What's the average delay?', 'Which airline has most delays?', 'Show peak hours'...">
            <button onclick="processQuery()" class="query-btn">Ask Question</button>
            <button onclick="clearQuery()" class="query-btn" style="background: #6c757d;">Clear</button>
            
            <div class="sample-queries">
                <strong>Sample Questions:</strong>
                <span class="sample-query" onclick="setQuery('What is the average departure delay?')">Average delay?</span>
                <span class="sample-query" onclick="setQuery('Which airline has the best on-time performance?')">Best airline?</span>
                <span class="sample-query" onclick="setQuery('What are the peak hours for flights?')">Peak hours?</span>
                <span class="sample-query" onclick="setQuery('How many flights were severely delayed?')">Severe delays?</span>
                <span class="sample-query" onclick="setQuery('Show weekend vs weekday performance')">Weekend vs weekday?</span>
            </div>
            
            <div id="queryResult" class="query-result" style="display: none;"></div>
        </div>
        
        <!-- Statistics Cards -->
        <div class="stats-grid">
            {self._create_stats_cards_html()}
        </div>
        
        <!-- Charts -->
        <div class="charts-container">
            {charts_html}
        </div>
    </div>
    
    <script>
        // Flight data for NLP processing
        const flightData = {data_json};
        const analysisResults = {json.dumps(self.analysis_results, default=str)};
        
        {self._get_nlp_javascript()}
    </script>
</body>
</html>
"""
        return html_template
    
    def _create_stats_cards_html(self):
        """Create HTML for statistics cards"""
        stats = self.analysis_results.get('basic_stats', {})
        efficiency = self.analysis_results.get('efficiency_metrics', {})
        
        cards_html = f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('total_flights', 0):,}</div>
            <div class="stat-label">Total Flights</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{efficiency.get('on_time_performance', 0)*100:.1f}%</div>
            <div class="stat-label">On-Time Performance</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats.get('avg_daily_flights', 0):.0f}</div>
            <div class="stat-label">Avg Daily Flights</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats.get('unique_airlines', 0)}</div>
            <div class="stat-label">Airlines</div>
        </div>
        """
        
        # Add delay statistics if available
        if 'delay_analysis' in self.analysis_results:
            delay_info = self.analysis_results['delay_analysis']
            if 'Departure Delay (min)' in delay_info:
                avg_delay = delay_info['Departure Delay (min)']['mean']
                cards_html += f"""
                <div class="stat-card">
                    <div class="stat-number">{avg_delay:.1f}</div>
                    <div class="stat-label">Avg Delay (min)</div>
                </div>
                """
        
        # Add cascade impact if available
        if 'cascade_analysis' in self.analysis_results:
            cascade_info = self.analysis_results['cascade_analysis']
            affected = cascade_info.get('affected_flights', 0)
            cards_html += f"""
            <div class="stat-card">
                <div class="stat-number">{affected}</div>
                <div class="stat-label">Cascade Affected</div>
            </div>
            """
        
        return cards_html
    
    def _create_all_charts(self):
        """Create all visualization charts"""
        charts = []
        
        # Chart 1: Hourly Operations
        if 'Departure Hour' in self.df.columns:
            fig1 = self._create_hourly_operations_chart()
            chart1_html = f"""
            <div class="chart">
                <h3>🕐 Hourly Flight Operations</h3>
                <div id="hourlyChart">{pyo.plot(fig1, output_type='div', include_plotlyjs=False)}</div>
            </div>
            """
            charts.append(chart1_html)
        
        # Chart 2: Delay Distribution
        if 'Departure Delay (min)' in self.df.columns:
            fig2 = self._create_delay_distribution_chart()
            chart2_html = f"""
            <div class="chart">
                <h3>📊 Delay Distribution Analysis</h3>
                <div id="delayChart">{pyo.plot(fig2, output_type='div', include_plotlyjs=False)}</div>
            </div>
            """
            charts.append(chart2_html)
        
        # Chart 3: Airline Performance
        if 'Airline' in self.df.columns and 'On Time' in self.df.columns:
            fig3 = self._create_airline_performance_chart()
            chart3_html = f"""
            <div class="chart">
                <h3>🏢 Airline Performance Comparison</h3>
                <div id="airlineChart">{pyo.plot(fig3, output_type='div', include_plotlyjs=False)}</div>
            </div>
            """
            charts.append(chart3_html)
        
        # Chart 4: Daily Trends
        if 'Date' in self.df.columns:
            fig4 = self._create_daily_trends_chart()
            chart4_html = f"""
            <div class="chart">
                <h3>📅 Daily Flight Trends</h3>
                <div id="dailyChart">{pyo.plot(fig4, output_type='div', include_plotlyjs=False)}</div>
            </div>
            """
            charts.append(chart4_html)
        
        # Chart 5: Delay Heatmap by Hour and Day
        if 'Departure Hour' in self.df.columns and 'Day of Week' in self.df.columns and 'Departure Delay (min)' in self.df.columns:
            fig5 = self._create_delay_heatmap()
            chart5_html = f"""
            <div class="chart">
                <h3>🔥 Delay Heatmap: Hour vs Day of Week</h3>
                <div id="heatmapChart">{pyo.plot(fig5, output_type='div', include_plotlyjs=False)}</div>
            </div>
            """
            charts.append(chart5_html)
        
        return '\n'.join(charts)
    
    def _create_hourly_operations_chart(self):
        """Create hourly operations chart"""
        hourly_data = self.df.groupby('Departure Hour').agg({
            'Flight Number': 'count',
            'Departure Delay (min)': 'mean'
        }).reset_index()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add bar chart for flight counts
        fig.add_trace(
            go.Bar(
                x=hourly_data['Departure Hour'],
                y=hourly_data['Flight Number'],
                name='Flight Count',
                opacity=0.7,
                marker_color='lightblue'
            ),
            secondary_y=False
        )
        
        # Add line chart for average delays
        fig.add_trace(
            go.Scatter(
                x=hourly_data['Departure Hour'],
                y=hourly_data['Departure Delay (min)'],
                mode='lines+markers',
                name='Avg Delay (min)',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ),
            secondary_y=True
        )
        
        fig.update_xaxes(title_text="Hour of Day")
        fig.update_yaxes(title_text="Number of Flights", secondary_y=False)
        fig.update_yaxes(title_text="Average Delay (minutes)", secondary_y=True)
        
        fig.update_layout(
            height=500,
            hovermode='x unified',
            legend=dict(x=0.01, y=0.99)
        )
        
        return fig
    
    def _create_delay_distribution_chart(self):
        """Create delay distribution chart"""
        delay_data = self.df['Departure Delay (min)'].dropna()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Delay Distribution', 'Delay by Day of Week'),
            specs=[[{"type": "histogram"}, {"type": "box"}]]
        )
        
        # Histogram
        fig.add_trace(
            go.Histogram(
                x=delay_data,
                nbinsx=30,
                name='Delay Distribution',
                marker_color='lightcoral',
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # Box plot by day of week
        if 'Day of Week' in self.df.columns:
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day in day_order:
                if day in self.df['Day of Week'].values:
                    day_data = self.df[self.df['Day of Week'] == day]['Departure Delay (min)'].dropna()
                    fig.add_trace(
                        go.Box(
                            y=day_data,
                            name=day,
                            boxpoints='outliers'
                        ),
                        row=1, col=2
                    )
        
        # Add vertical line for mean in histogram
        fig.add_vline(
            x=delay_data.mean(),
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {delay_data.mean():.1f} min",
            row=1, col=1
        )
        
        fig.update_layout(height=500, showlegend=False)
        
        return fig
    
    def _create_airline_performance_chart(self):
        """Create airline performance chart"""
        airline_data = self.df.groupby('Airline').agg({
            'Flight Number': 'count',
            'On Time': 'mean',
            'Departure Delay (min)': 'mean'
        }).reset_index()
        
        # Filter airlines with significant operations
        airline_data = airline_data[airline_data['Flight Number'] >= 10]
        airline_data = airline_data.head(10).sort_values('On Time', ascending=True)
        
        fig = go.Figure()
        
        # Create color scale based on performance
        colors = airline_data['On Time'].apply(
            lambda x: 'red' if x < 0.7 else 'orange' if x < 0.85 else 'green'
        )
        
        fig.add_trace(go.Bar(
            y=airline_data['Airline'],
            x=airline_data['On Time'] * 100,
            orientation='h',
            marker_color=colors,
            text=airline_data['On Time'].apply(lambda x: f'{x*100:.1f}%'),
            textposition='inside',
            hovertemplate='<b>%{y}</b><br>On-Time: %{x:.1f}%<br>Flights: %{customdata}<extra></extra>',
            customdata=airline_data['Flight Number']
        ))
        
        fig.update_layout(
            title='Airline On-Time Performance',
            xaxis_title='On-Time Performance (%)',
            yaxis_title='Airline',
            height=500
        )
        
        return fig
    
    def _create_daily_trends_chart(self):
        """Create daily trends chart"""
        daily_data = self.df.groupby(self.df['Date'].dt.date).agg({
            'Flight Number': 'count',
            'Departure Delay (min)': 'mean',
            'On Time': 'mean'
        }).reset_index()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily Flight Volume', 'Daily Performance Metrics'),
            specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
        )
        
        # Daily flight counts
        fig.add_trace(
            go.Scatter(
                x=daily_data['Date'],
                y=daily_data['Flight Number'],
                mode='lines+markers',
                name='Daily Flights',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Daily performance metrics
        fig.add_trace(
            go.Scatter(
                x=daily_data['Date'],
                y=daily_data['On Time'] * 100,
                mode='lines+markers',
                name='On-Time %',
                line=dict(color='green', width=2)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=daily_data['Date'],
                y=daily_data['Departure Delay (min)'],
                mode='lines+markers',
                name='Avg Delay (min)',
                line=dict(color='red', width=2),
                yaxis='y4'
            ),
            row=2, col=1,
            secondary_y=True
        )
        
        fig.update_layout(height=600)
        fig.update_yaxes(title_text="Number of Flights", row=1, col=1)
        fig.update_yaxes(title_text="On-Time Performance (%)", row=2, col=1)
        fig.update_yaxes(title_text="Average Delay (min)", row=2, col=1, secondary_y=True)
        
        return fig
    
    def _create_delay_heatmap(self):
        """Create delay heatmap by hour and day of week"""
        # Create pivot table for heatmap
        heatmap_data = self.df.pivot_table(
            values='Departure Delay (min)',
            index='Day of Week',
            columns='Departure Hour',
            aggfunc='mean'
        )
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(day_order)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='RdYlGn_r',
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>Hour: %{x}<br>Avg Delay: %{z:.1f} min<extra></extra>'
        ))
        
        fig.update_layout(
            title='Average Delay by Hour and Day of Week',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=400
        )
        
        return fig
    
    def _prepare_data_for_nlp(self):
        """Prepare data for NLP queries"""
        # Create a simplified version of the data for JavaScript processing
        data_summary = {
            'total_flights': len(self.df),
            'columns': list(self.df.columns),
            'date_range': {
                'start': self.df['Date'].min().isoformat() if 'Date' in self.df.columns else None,
                'end': self.df['Date'].max().isoformat() if 'Date' in self.df.columns else None
            }
        }
        
        # Add summary statistics for key columns
        if 'Departure Delay (min)' in self.df.columns:
            delay_data = self.df['Departure Delay (min)'].dropna()
            data_summary['delay_stats'] = {
                'mean': float(delay_data.mean()),
                'median': float(delay_data.median()),
                'std': float(delay_data.std()),
                'min': float(delay_data.min()),
                'max': float(delay_data.max())
            }
        
        if 'Airline' in self.df.columns:
            data_summary['airlines'] = self.df['Airline'].value_counts().to_dict()
        
        if 'On Time' in self.df.columns:
            data_summary['on_time_rate'] = float(self.df['On Time'].mean())
        
        if 'Departure Hour' in self.df.columns:
            hourly_counts = self.df['Departure Hour'].value_counts().sort_index()
            data_summary['hourly_flights'] = hourly_counts.to_dict()
        
        return json.dumps(data_summary, default=str)
    
    def _get_nlp_javascript(self):
        """Generate JavaScript code for NLP query processing"""
        return '''
        function setQuery(query) {
            document.getElementById('queryInput').value = query;
        }
        
        function clearQuery() {
            document.getElementById('queryInput').value = '';
            document.getElementById('queryResult').style.display = 'none';
        }
        
        function processQuery() {
            const query = document.getElementById('queryInput').value.toLowerCase().trim();
            const resultDiv = document.getElementById('queryResult');
            
            if (!query) {
                resultDiv.innerHTML = '<p>Please enter a question about the flight data.</p>';
                resultDiv.style.display = 'block';
                return;
            }
            
            let response = '';
            
            // Pattern matching for different types of queries
            if (query.includes('average delay') || query.includes('avg delay') || query.includes('mean delay')) {
                if (flightData.delay_stats) {
                    response = `The average departure delay is <strong>${flightData.delay_stats.mean.toFixed(1)} minutes</strong>. The median delay is ${flightData.delay_stats.median.toFixed(1)} minutes.`;
                } else {
                    response = 'Delay information is not available in the dataset.';
                }
            }
            else if (query.includes('on-time') || query.includes('on time') || query.includes('punctual')) {
                if (flightData.on_time_rate) {
                    response = `The overall on-time performance is <strong>${(flightData.on_time_rate * 100).toFixed(1)}%</strong>.`;
                } else {
                    response = 'On-time performance data is not available.';
                }
            }
            else if (query.includes('total flights') || query.includes('how many flights') || query.includes('number of flights')) {
                response = `There are <strong>${flightData.total_flights.toLocaleString()} total flights</strong> in the dataset.`;
            }
            else if (query.includes('airlines') || query.includes('which airline')) {
                if (flightData.airlines) {
                    const airlines = Object.keys(flightData.airlines);
                    const topAirline = airlines[0];
                    const topCount = flightData.airlines[topAirline];
                    response = `There are <strong>${airlines.length} different airlines</strong> in the data. The most frequent airline is <strong>${topAirline}</strong> with ${topCount} flights.`;
                } else {
                    response = 'Airline information is not available in the dataset.';
                }
            }
            else if (query.includes('peak hour') || query.includes('busiest hour') || query.includes('busy time')) {
                if (flightData.hourly_flights) {
                    const hours = Object.keys(flightData.hourly_flights);
                    const counts = Object.values(flightData.hourly_flights);
                    const maxIndex = counts.indexOf(Math.max(...counts));
                    const peakHour = hours[maxIndex];
                    const peakCount = counts[maxIndex];
                    response = `The busiest hour is <strong>${peakHour}:00</strong> with ${peakCount} flights.`;
                } else {
                    response = 'Hourly flight data is not available.';
                }
            }
            else if (query.includes('worst delay') || query.includes('maximum delay') || query.includes('longest delay')) {
                if (flightData.delay_stats) {
                    response = `The worst recorded delay was <strong>${flightData.delay_stats.max.toFixed(1)} minutes</strong>.`;
                } else {
                    response = 'Delay statistics are not available.';
                }
            }
            else if (query.includes('date range') || query.includes('time period') || query.includes('when')) {
                if (flightData.date_range && flightData.date_range.start) {
                    response = `The data covers the period from <strong>${flightData.date_range.start}</strong> to <strong>${flightData.date_range.end}</strong>.`;
                } else {
                    response = 'Date range information is not available.';
                }
            }
            else if (query.includes('standard deviation') || query.includes('variability') || query.includes('variation')) {
                if (flightData.delay_stats) {
                    response = `The standard deviation of delays is <strong>${flightData.delay_stats.std.toFixed(1)} minutes</strong>, indicating ${flightData.delay_stats.std > 30 ? 'high' : 'moderate'} variability in delays.`;
                } else {
                    response = 'Delay variability data is not available.';
                }
            }
            else if (query.includes('summary') || query.includes('overview') || query.includes('key metrics')) {
                let summary = `<strong>Flight Data Summary:</strong><br>`;
                summary += `• Total Flights: ${flightData.total_flights.toLocaleString()}<br>`;
                if (flightData.on_time_rate) {
                    summary += `• On-Time Performance: ${(flightData.on_time_rate * 100).toFixed(1)}%<br>`;
                }
                if (flightData.delay_stats) {
                    summary += `• Average Delay: ${flightData.delay_stats.mean.toFixed(1)} minutes<br>`;
                }
                if (flightData.airlines) {
                    summary += `• Number of Airlines: ${Object.keys(flightData.airlines).length}<br>`;
                }
                response = summary;
            }
            else {
                // Default response with available options
                response = `I can help you with questions about:<br>
                    • Average delays and delay statistics<br>
                    • On-time performance rates<br>
                    • Total number of flights<br>
                    • Airline information<br>
                    • Peak hours and busy times<br>
                    • Date ranges and time periods<br>
                    • Data summary and key metrics<br><br>
                    Try asking: "What's the average delay?" or "Which airline has the most flights?"`;
            }
            
            resultDiv.innerHTML = response;
            resultDiv.style.display = 'block';
        }
        
        // Allow Enter key to submit query
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processQuery();
            }
        });
        '''