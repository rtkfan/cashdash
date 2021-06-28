import config
import sqlite3
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

con = sqlite3.connect(config.CONFIG_DB_LOCATION)

with open('./queries/get_expenses_by_payment_account.sql') as f:
    query = f.read()

df = pd.read_sql_query(query,con)

df_agg = df[df["expense_type"]=='EXPENSE'].groupby(by=["expense_category"],
                                                   as_index=False)["amount_cents"].sum()

df_agg.sort_values("amount_cents", inplace=True, ascending=False)

df_agg["amount_dollars"] = df_agg["amount_cents"]/100.0


app = dash.Dash(__name__)

fig = px.bar(df_agg, x="expense_category", y="amount_dollars", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Expenses'),

    html.Div(children='''
        Hello world, but for graphs.
    '''),

    dcc.Graph(
        id='example-income_statement',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
