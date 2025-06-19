import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------- file path ----------
DATA_PATH = Path("assets/porsche718gt4_daytona_road_20250619_ Stint_1.csv")

# ---------- 1.  METADATA (rows 0-11) ----------
meta_lines = []
with DATA_PATH.open() as f:
    for _ in range(12):
        meta_lines.append(next(f).strip().split(','))

metadata = []
for row in meta_lines:
    # left-hand pair
    if len(row) >= 2 and row[0] and row[1]:
        metadata.append((row[0].strip('"'), row[1].strip('"')))
    # right-hand pair (if present)
    if len(row) >= 5 and row[4] and row[5]:
        metadata.append((row[4].strip('"'), row[5].strip('"')))

# ---------- 2.  HEADERS & UNITS ----------
# read header row (12) and unit row (13) as raw strings
header_row = (
    pd.read_csv(DATA_PATH, skiprows=12, nrows=1, header=None, dtype=str)
      .iloc[0]
      .str.replace('"', '')
)

unit_row = (
    pd.read_csv(DATA_PATH, skiprows=13, nrows=1, header=None, dtype=str)
      .iloc[0]
      .str.replace('"', '')
)

# drop empty headers & build clean lists / dicts
headers = []
units = {}
for col_name, unit in zip(header_row, unit_row):
    if pd.notna(col_name) and col_name != "":
        headers.append(col_name)
        units[col_name] = unit

# ---------- 3.  DATA ----------
df = pd.read_csv(DATA_PATH, skiprows=14, header=None, names=headers)

numeric_df = df.select_dtypes(include="number")
valid_columns = [c for c in numeric_df.columns if c in units]

# ---------- 4.  DASH APP ----------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "iRacing Telemetry Dashboard"

app.layout = dbc.Container(
    [
        html.H2("Porsche 718 GT4 – MoTeC Telemetry", className="my-3"),

        # session metadata table
        html.H4("Session Metadata"),
        dbc.Table(
            [
                html.Thead(html.Tr([html.Th("Key"), html.Th("Value")])),
                html.Tbody([html.Tr([html.Td(k), html.Td(v)]) for k, v in metadata]),
            ],
            bordered=True,
            striped=True,
            size="sm",
            className="mb-4",
        ),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="column-dropdown",
                            options=[
                                {"label": f"{c} ({units.get(c,'')})", "value": c}
                                for c in valid_columns
                            ],
                            value=valid_columns[0],
                            clearable=False,
                        ),
                        html.Div(id="summary-output", className="mt-3"),
                    ],
                    md=4,
                ),
                dbc.Col(dcc.Graph(id="telemetry-graph"), md=8),
            ]
        ),
    ],
    fluid=True,
)

# ---------- 5.  CALLBACK ----------
@app.callback(
    Output("summary-output", "children"),
    Output("telemetry-graph", "figure"),
    Input("column-dropdown", "value"),
)
def update_dashboard(column):
    series = numeric_df[column]
    stats = series.describe()
    unit = units.get(column, "")

    fig = px.line(df, x="Time", y=column, title=f"{column} Over Time ({unit})")
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))

    summary = html.Ul(
        [
            html.Li(f"Mean : {stats['mean']:.3f} {unit}"),
            html.Li(f"Min  : {stats['min']:.3f} {unit}"),
            html.Li(f"Max  : {stats['max']:.3f} {unit}"),
            html.Li(f"Std  : {stats['std']:.3f} {unit}"),
            html.Li(f"Samples: {int(stats['count'])}"),
        ]
    )
    return summary, fig


if __name__ == "__main__":
    app.run(debug=True)
