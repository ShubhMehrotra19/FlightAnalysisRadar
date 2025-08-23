import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DashboardGenerator:
    """Generate interactive web dashboard"""
    
    def __init__(self, config):
        self.config = config
        self.app = None
        self.df = None
        self.analysis_results = None
        
    def create_dashboard(self, df, analysis_results):
        """Create and launch interactive dashboard"""
        self.df = df
        self.analysis_results = analysis_results
        
        self.app = dash.Dash(__name__)
        
        self.app.layout = html.Div([
            html.H1("✈ Flight Operations Dashboard", 
                   style={'textAlign': 'center', 'marginBottom': 30}),
            
            # Summary cards
            self._create_summary_cards(),
            
            # Charts
            dcc.Graph(id='hourly-operations'),
            dcc.Graph(id='delay-analysis'),
            dcc.Graph(id='airline-performance'),
            
        ])
        
        self._setup_callbacks()
        
        # Start dashboard server
        port = self.config.get('dashboard_port', 8050)
        try:
            self.app.run_server(debug=False, port=port, host='127.0.0.1')
        except Exception as e:
            logger.warning(f"Dashboard server failed to start: {e}")
        
        return f"http://127.0.0.1:{port}"
    
    def _create_summary_cards(self):
        """Create summary statistics cards"""
        stats = self.analysis_results.get('basic_stats', {})
        efficiency = self.analysis_results.get('efficiency_metrics', {})
        
        cards = html.Div([
            html.Div([
                html.H3(f"{stats.get('total_flights', 0):,}"),
                html.P("Total Flights")
            ], className='summary-card', style={'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'backgroundColor': '#f0f0f0', 'borderRadius': '10px', 'textAlign': 'center', 'minWidth': '150px'}),
            
            html.Div([
                html.H3(f"{efficiency.get('on_time_performance', 0)*100:.1f}%"),
                html.P("On-Time Performance")
            ], className='summary-card', style={'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'backgroundColor': '#f0f0f0', 'borderRadius': '10px', 'textAlign': 'center', 'minWidth': '150px'}),
            
            html.Div([
                html.H3(f"{stats.get('avg_daily_flights', 0):.0f}"),
                html.P("Avg Daily Flights")
            ], className='summary-card', style={'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'backgroundColor': '#f0f0f0', 'borderRadius': '10px', 'textAlign': 'center', 'minWidth': '150px'}),
            
            html.Div([
                html.H3(f"{stats.get('unique_airlines', 0)}"),
                html.P("Airlines")
            ], className='summary-card', style={'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'backgroundColor': '#f0f0f0', 'borderRadius': '10px', 'textAlign': 'center', 'minWidth': '150px'}),
        ], style={'textAlign': 'center', 'marginBottom': '30px'})
        
        return cards
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks for interactivity"""
        
        @self.app.callback(
            Output('hourly-operations', 'figure'),
            Input('hourly-operations', 'id')
        )
        def update_hourly_chart(_):
            if 'Departure Hour' in self.df.columns:
                hourly_data = self.df.groupby('Departure Hour').agg({
                    'Flight Number': 'count',
                    'Departure Delay (min)': 'mean'
                }).reset_index()
                
                fig = go.Figure()
                
                # Add bar chart for flight counts
                fig.add_trace(go.Bar(
                    x=hourly_data['Departure Hour'],
                    y=hourly_data['Flight Number'],
                    name='Flight Count',
                    yaxis='y',
                    opacity=0.7
                ))
                
                # Add line chart for average delays
                if 'Departure Delay (min)' in hourly_data.columns:
                    fig.add_trace(go.Scatter(
                        x=hourly_data['Departure Hour'],
                        y=hourly_data['Departure Delay (min)'],
                        mode='lines+markers',
                        name='Avg Delay (min)',
                        yaxis='y2',
                        line=dict(color='red')
                    ))
                
                fig.update_layout(
                    title='Hourly Flight Operations',
                    xaxis_title='Hour of Day',
                    yaxis=dict(title='Number of Flights', side='left'),
                    yaxis2=dict(title='Average Delay (minutes)', side='right', overlaying='y'),
                    hovermode='x'
                )
                
                return fig
            
            return go.Figure()
        
        @self.app.callback(
            Output('delay-analysis', 'figure'),
            Input('delay-analysis', 'id')
        )
        def update_delay_chart(_):
            if 'Departure Delay (min)' in self.df.columns:
                delay_data = self.df['Departure Delay (min)'].dropna()
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=delay_data,
                    nbinsx=30,
                    name='Delay Distribution',
                    opacity=0.7
                ))
                
                # Add vertical line for mean
                if len(delay_data) > 0:
                    fig.add_vline(
                        x=delay_data.mean(),
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Mean: {delay_data.mean():.1f} min"
                    )
                
                fig.update_layout(
                    title='Departure Delay Distribution',
                    xaxis_title='Delay (minutes)',
                    yaxis_title='Frequency'
                )
                
                return fig
            
            return go.Figure()
        
        @self.app.callback(
            Output('airline-performance', 'figure'),
            Input('airline-performance', 'id')
        )
        def update_airline_chart(_):
            if 'Airline' in self.df.columns and 'On Time' in self.df.columns:
                airline_perf = self.df.groupby('Airline').agg({
                    'Flight Number': 'count',
                    'On Time': 'mean'
                }).reset_index()
                
                # Filter to show only airlines with significant operations
                airline_perf = airline_perf[airline_perf['Flight Number'] >= 10]
                airline_perf = airline_perf.head(10)
                
                if len(airline_perf) > 0:
                    fig = px.bar(
                        airline_perf,
                        x='Airline',
                        y='On Time',
                        title='Airline On-Time Performance',
                        labels={'On Time': 'On-Time Rate'},
                        color='On Time',
                        color_continuous_scale='RdYlGn'
                    )
                    
                    fig.update_layout(yaxis_tickformat='%')
                    
                    return fig
            
            return go.Figure()