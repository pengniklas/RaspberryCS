import sqlite3
import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Dash starten
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Wetterstation"


# Sensordaten aus Datenbank abrufen
def get_sensor_data():
    conn = sqlite3.connect('sensor_data.db')
    query = "SELECT timestamp, temperature, humidity, liquid_level, uv_level FROM sensor_data ORDER BY timestamp DESC LIMIT 50"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# Layout
app.layout = dbc.Container([
    html.H1("Wetterstation", className="my-4"),
    
    dbc.Row([
        dbc.Col([
            html.H3("Sensorendaten"),
            html.Div(id="data-table")
        ], width=6),
        dbc.Col([
            html.H3("Visualisierungen"),
            dcc.Graph(id="temperature-graph"),
            dcc.Graph(id="humidity-graph"),
            dcc.Graph(id="liquid-level-graph"),
            dcc.Graph(id="uv-level-graph"),
        ], width=6),
    ]),
    
    # Automatische Aktualisierung (10s)
    dcc.Interval(
        id="interval-component",
        interval=10000,  
        n_intervals=0 # Reset
    )
], fluid=True)

# Daten aktualisieren
@app.callback(
    [Output("data-table", "children"),
     Output("temperature-graph", "figure"),
     Output("humidity-graph", "figure"),
     Output("liquid-level-graph", "figure"),
     Output("uv-level-graph", "figure")],
    [Input("interval-component", "n_intervals")]
)

def update_dashboard(n_intervals):
    df = get_sensor_data()

    # Spaltennamen anpassen
    df.columns = ["Datum/Uhrzeit", "Temperatur (°C)", "Luftfeuchtigkeit (%)", "Niederschlag", "Sonnenlicht"]

    # Tabelle 
    table = dbc.Table.from_dataframe(
        df, striped=True, bordered=True, hover=True, responsive=True
    )

    # Diagramm Temperatur
    temperature = {
        "data": [
            {"x": df["Datum/Uhrzeit"], "y": df["Temperatur (°C)"], "type": "line", "name": "Temperatur (°C)"},
        ],
        "layout": {"title": "Temperatur"}
    }

    # Diagramm Luftfeuchtigkeit
    humidity = {
        "data": [
            {"x": df["Datum/Uhrzeit"], "y": df["Luftfeuchtigkeit (%)"], "type": "line", "name": "Luftfeuchtigkeit (%)"},
        ],
        "layout": {"title": "Luftfeuchtigkeit"}
    }

    # Diagramm Niederschlag
    liquid_level = {
        "data": [
            {"x": df["Datum/Uhrzeit"], "y": df["Niederschlag"], "type": "line", "name": "Niederschlag"},
        ],
        "layout": {"title": "Niederschlag"}
    }

    # Diagramm Sonnenlicht
    uv_level = {
        "data": [
            {"x": df["Datum/Uhrzeit"], "y": df["Sonnenlicht"], "type": "line", "name": "Sonnenlicht"},
        ],
        "layout": {"title": "Sonnenlicht"}
    }

    return table, temperature, humidity, liquid_level, uv_level


# App ausführen
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=5000, debug=True)
