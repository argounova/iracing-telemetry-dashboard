import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Load your clean CSV
df = pd.read_csv("assets/porsche718gt4_daytona_road_20250619_ Stint_1.csv", skiprows=[1])
units = pd.read_csv("assets/porsche718gt4_daytona_road_20250619_ Stint_1.csv", nrows=1).iloc[0].to_dict()
numeric_df = df.select_dtypes(include='number')
valid_columns = [col for col in numeric_df.columns if not col.startswith("Unnamed")]

# Setup Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "718 GT4 Telemetry Dashboard"

app.layout = dbc.Container([
    html.H2("Porsche 718 GT4 - MoTeC Telemetry", className="my-3"),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='column-dropdown',
                options=[{'label': f'{col} ({units[col]})', 'value': col} for col in valid_columns],
                value=valid_columns[0],
                clearable=False
            ),
            html.Div(id='summary-output', className="mt-3")
        ], md=4),

        dbc.Col([
            dcc.Graph(id='telemetry-graph')
        ], md=8),
    ])
], fluid=True)

@app.callback(
    Output('summary-output', 'children'),
    Output('telemetry-graph', 'figure'),
    Input('column-dropdown', 'value')
)
def update_dashboard(column):
    series = numeric_df[column]
    stats = series.describe()
    unit = units.get(column, '')

    fig = px.line(df, x='Time', y=column, title=f'{column} Over Time ({unit})')
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))

    summary = html.Ul([
        html.Li(f"Mean: {stats['mean']:.3f} {unit}"),
        html.Li(f"Min: {stats['min']:.3f} {unit}"),
        html.Li(f"Max: {stats['max']:.3f} {unit}"),
        html.Li(f"Std Dev: {stats['std']:.3f} {unit}"),
        html.Li(f"Samples: {int(stats['count'])}")
    ])
    return summary, fig

if __name__ == '__main__':
    app.run(debug=True)
