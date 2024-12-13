import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

# Load your dataset
file_path = "./sample 2024.xlsx"  # Replace with your actual file path
df = pd.read_excel(file_path)

# Define column groups for the Y-axis
stages = ['Qualification', 'Presentation', 'Proof of Concept', 'Proposal/Price Quote',
          'Legal Review', 'Negotiation', 'Closed Won']

# Preprocess data: Get unique values for filters
fiscal_year_options = df['Fiscal Year'].dropna().unique()
opportunity_type_options = df['Opportunity Type'].dropna().unique()
final_source_options = df['Final Source'].dropna().unique()
theatre_options = df['S2 Theatre'].dropna().unique()
region_options = df['S2 Region'].dropna().unique()
industry_options = df['Industry'].fillna("N/A").unique().tolist()

# Initialize the Dash app
app = Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1("Funnel Chart and Pivot Tables", style={'text-align': 'center'}),
    dcc.RadioItems(
        id='x-axis-toggle',
        options=[
            {'label': 'Industry', 'value': 'Industry'},
            {'label': 'Final Source', 'value': 'Final Source'}
        ],
        value='Industry',  # Default to Industry
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    ),
    dcc.RadioItems(
        id='y-axis-toggle',
        options=[
            {'label': 'Counts', 'value': 'counts'},
            {'label': 'Dollar Amounts', 'value': 'dollars'}
        ],
        value='counts',  # Default to counts
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    ),
    dcc.Dropdown(
        id='industry-dropdown',
        options=[{'label': industry, 'value': industry} for industry in industry_options],
        multi=True,
        value=industry_options,  # Default: all industries selected
        placeholder="Select industries...",
    ),
    dcc.Dropdown(
        id='theatre-dropdown',
        options=[{'label': theatre, 'value': theatre} for theatre in theatre_options],
        multi=True,
        value=theatre_options,  # Default: all theatres selected
        placeholder="Select theatres...",
    ),
    dcc.Dropdown(
        id='region-dropdown',
        options=[{'label': region, 'value': region} for region in region_options],
        multi=True,
        value=region_options,  # Default: all regions selected
        placeholder="Select regions...",
    ),
    dcc.Dropdown(
        id='fiscal-year-dropdown',
        options=[{'label': year, 'value': year} for year in fiscal_year_options],
        multi=True,
        value=fiscal_year_options,  # Default: all fiscal years selected
        placeholder="Select fiscal years...",
    ),
    dcc.Dropdown(
        id='opportunity-type-dropdown',
        options=[{'label': opp_type, 'value': opp_type} for opp_type in opportunity_type_options],
        multi=True,
        value=opportunity_type_options,  # Default: all opportunity types selected
        placeholder="Select opportunity types...",
    ),
    dcc.Dropdown(
        id='final-source-dropdown',
        options=[{'label': source, 'value': source} for source in final_source_options],
        multi=True,
        value=final_source_options,  # Default: all final sources selected
        placeholder="Select final sources...",
    ),
    dcc.Graph(id='funnel-chart'),
    html.Div(id='pivot-table', style={'margin-top': '20px'}),
    html.Div(id='percentage-table', style={'margin-top': '20px'})
])

# Callback to update the funnel chart and tables
@app.callback(
    [Output('funnel-chart', 'figure'),
     Output('pivot-table', 'children'),
     Output('percentage-table', 'children')],
    [Input('x-axis-toggle', 'value'),
     Input('y-axis-toggle', 'value'),
     Input('industry-dropdown', 'value'),
     Input('theatre-dropdown', 'value'),
     Input('region-dropdown', 'value'),
     Input('fiscal-year-dropdown', 'value'),
     Input('opportunity-type-dropdown', 'value'),
     Input('final-source-dropdown', 'value')]
)
def update_charts(x_axis_choice, y_axis_choice, selected_industries, selected_theatres, selected_regions,
                  selected_fiscal_years, selected_opportunity_types, selected_final_sources):
    # Select appropriate column set based on the Y-axis toggle
    if y_axis_choice == 'counts':
        y_axis_columns = stages
    else:
        y_axis_columns = [col + ' $' for col in stages]

    # Filter the data based on selections
    filtered_data = df[
        df['Industry'].fillna("N/A").isin(selected_industries) &
        df['S2 Theatre'].isin(selected_theatres) &
        df['S2 Region'].isin(selected_regions) &
        df['Fiscal Year'].isin(selected_fiscal_years) &
        df['Opportunity Type'].isin(selected_opportunity_types) &
        df['Final Source'].isin(selected_final_sources)
    ]

    # Group by the selected X-axis column
    grouped_data = filtered_data.groupby(x_axis_choice)[y_axis_columns].sum()

    # Create the funnel chart
    funnel_fig = go.Figure()

    for group in grouped_data.index:
        funnel_fig.add_trace(go.Funnel(
            name=group,
            y=stages,
            x=grouped_data.loc[group].tolist(),
            textinfo="value+percent initial"
        ))

    funnel_fig.update_layout(
        title=f"Funnel Chart ({'Counts' if y_axis_choice == 'counts' else 'Dollar Amounts'}) Grouped by {x_axis_choice}",
        xaxis_title="Value",
        yaxis_title="Stages",
    )

    # Prepare data for the pivot table (First Table)
    table_data = grouped_data.T.reset_index()
    table_headers = [x_axis_choice] + list(grouped_data.index)

    # Create the first pivot table
    table_html = html.Table(
        # Header
        [html.Tr([html.Th(header, style={'border': '1px solid black'}) for header in table_headers])] +
        # Body
        [html.Tr([
            html.Td(row[col], style={'border': '1px solid black', 'text-align': 'center'})
            for col in table_data.columns
        ]) for _, row in table_data.iterrows()],
        style={'border-collapse': 'collapse', 'width': '100%', 'text-align': 'center'}
    )

    # Calculate percentages for the percentage table (Second Table)
    # Normalize each stage as a percentage of the Qualification stage
    percentage_data = grouped_data.div(grouped_data['Qualification'], axis=0) * 100

    # Transpose to switch rows and columns
    percentage_data = percentage_data.T.reset_index()
    percentage_data.columns = ['Stages'] + list(grouped_data.index)

    # Create the percentage table
    percentage_html = html.Table(
        # Header
        [html.Tr([html.Th(header, style={'border': '1px solid black'}) for header in percentage_data.columns])] +
        # Body
        [html.Tr([
            html.Td(f"{row[col]:.0f}%" if isinstance(row[col], (int, float)) else row[col],
                    style={'border': '1px solid black', 'text-align': 'center'})
            for col in percentage_data.columns
        ]) for _, row in percentage_data.iterrows()],
        style={'border-collapse': 'collapse', 'width': '100%', 'text-align': 'center'}
    )

    return funnel_fig, table_html, percentage_html

# Run the app
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080)




    print("Dash app is running on http://127.0.0.1:8050/")
