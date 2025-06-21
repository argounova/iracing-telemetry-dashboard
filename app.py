import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
from pathlib import Path

# === FILE PATH ===
DATA_PATH = Path("assets/porsche718gt4_daytona_road_20250619_ Stint_1.csv")

# === METADATA ===
meta_lines = []
with DATA_PATH.open() as f:
    for _ in range(11):
        meta_lines.append(next(f).strip().split(','))

metadata = [
    (row[0].strip('"'), row[1].strip('"'))
    for row in meta_lines if len(row) >= 2 and row[0] and row[1]
]

# === HEADERS + UNITS ===
header_row = (
    pd.read_csv(DATA_PATH, skiprows=10, nrows=1, header=None, dtype=str)
    .iloc[0]
    .str.replace('"', '')
)

unit_row = (
    pd.read_csv(DATA_PATH, skiprows=11, nrows=1, header=None, dtype=str)
    .iloc[0]
    .str.replace('"', '')
)

headers = []
units = {}
for col_name, unit in zip(header_row, unit_row):
    if pd.notna(col_name) and col_name.strip() != "":
        headers.append(col_name)
        units[col_name] = unit

# === TELEMETRY DATA ===
df = pd.read_csv(DATA_PATH, skiprows=12, header=None, names=headers)
numeric_df = df.select_dtypes(include='number')
valid_columns = [col for col in numeric_df.columns if col in units]

# === DASH APP ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "iRacing Telemetry Dashboard"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Porsche 718 GT4 – MoTeC Telemetry",  className="my-1"),
            html.H4("iRacing Session Metadata",  className="mb-5", style={ 'color': '#ff1e8e' }),
            html.H4("Select a Parameter"),
            dcc.Dropdown(
                id="column-dropdown",
                options=[
                    {"label": f"{col} ({units.get(col, '')})", "value": col}
                    for col in valid_columns
                ],
                value=valid_columns[0] if valid_columns else None,
                placeholder="Select a channel..." if valid_columns else "No numeric telemetry columns found",
                disabled=not bool(valid_columns),
                clearable=False
            ),
            html.Div(id="summary-output", className="mt-3")
        ], md=6),
        dbc.Col([
            dbc.Table([
            html.Thead(html.Tr([html.Th("Key"), html.Th("Value")])),
            html.Tbody([html.Tr([html.Td(k), html.Td(v)]) for k, v in metadata])
            ], bordered=True, striped=True, size="sm", className="mb-4"),
        ], md=6),  
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="telemetry-graph", className='graph')
        ], md=12),
    ])
], fluid=True)

# === CALLBACK ===
@app.callback(
    Output("summary-output", "children"),
    Output("telemetry-graph", "figure"),
    Input("column-dropdown", "value")
)
def update_dashboard(column):
    if not column:
        return html.Div("No telemetry data available."), {}

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

if __name__ == "__main__":
    app.run(debug=True)