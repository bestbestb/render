import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import os

# Load your dataset
file_path = "./sample 2024.xlsx"  # Ensure this file is in the same directory
df = pd.read_excel(file_path)

# Define column groups for the Y-axis
stages = ['Qualification', 'Presentation', 'Proof of Concept', 'Proposal/Price Quote',
          'Legal Review', 'Negotiation', 'Closed Won']

# Preprocess data: Get unique values for filters
fiscal_year_options = df['Fiscal Year'].dropna().unique()
opportunity_type_options = df['Opportunity Type'].dropna().unique()
final_source_options = df['Final Source'].dropna().unique()
theatre_options = df['S2 Theatre'].fillna("Unknown").unique()
region_options = df['S2 Region'].fillna("Unknown").unique()
industry_options = df['Industry'].fillna("N/A").unique().tolist()

# Initialize the Dash app
app = Dash(__name__)
server = app.server  # Expose the Flask server for Gunicorn

# Layout of the app
app.layout = html.Div([
    html.H1("Funnel Chart and Pivot Tables", style={'text-align': 'center'}),
    dcc.RadioItems(
        id='x-axis-toggle',
        options=[
            {'label': 'Industry', 'value': 'Industry'},
            {'label': 'Final Source', 'value': 'Final Source'}
        ],
        value='Industry',
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    ),
    dcc.RadioItems(
        id='y-axis-toggle',
        options=[
            {'label': 'Counts', 'value': 'counts'},
            {'label': 'Dollar Amounts', 'value': 'dollars'}
        ],
        value='counts',
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    ),
    dcc.Dropdown(
        id='industry-dropdown',
        options=[{'label': industry, 'value': industry} for industry in industry_options],
        multi=True,
        value=industry_options,
        placeholder="Select industries...",
    ),
    dcc.Dropdown(
        id='theatre-dropdown',
        options=[{'label': theatre, 'value': theatre} for theatre in theatre_options],
        multi=True,
        value=theatre_options,
        placeholder="Select theatres...",
    ),
    dcc.Dropdown(
        id='region-dropdown',
        options=[{'label': region, 'value': region} for region in region_options],
        multi=True,
        value=region_options,
        placeholder="Select regions...",
    ),
    dcc.Dropdown(
        id='fiscal-year-dropdown',
        options=[{'label': year, 'value': year} for year in fiscal_year_options],
        multi=True,
        value=fiscal_year_options,
        placeholder="Select fiscal years...",
    ),
    dcc.Dropdown(
        id='opportunity-type-dropdown',
        options=[{'label': opp_type, 'value': opp_type} for opp_type in opportunity_type_options],
        multi=True,
        value=opportunity_type_options,
        placeholder="Select opportunity types...",
    ),
    dcc.Dropdown(
        id='final-source-dropdown',
        options=[{'label': source, 'value': source} for source in final_source_options],
        multi=True,
        value=final_source_options,
        placeholder="Select final sources...",
    ),
    dcc.Graph(id='funnel-chart'),
    html.Div(id='pivot-table', style={'margin-top': '20px'}),
    html.Div(id='percentage-table', style={'margin-top': '20px'})
])

# Callback logic remains unchanged...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Handle dynamic port binding
    app.run_server(host="0.0.0.0", port=port)
