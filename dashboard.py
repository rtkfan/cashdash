import config
import sqlite3
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

def get_data(path):
    con = sqlite3.connect(config.CONFIG_DB_LOCATION)
    with open(path) as f:
        query = f.read()
    df = pd.read_sql_query(query,con)
    con.close()
    return df

splits = get_data('./queries/get_expenses_by_payment_account.sql')
accounts = get_data('./queries/get_account_full_paths.sql')

df_agg = splits[splits["expense_type"]=='EXPENSE'].groupby(by=["expense_category","expense_account_guid"],
                                                   as_index=False)["amount_cents"].sum()
df_agg.sort_values("amount_cents", inplace=True, ascending=False)
df_agg["amount_dollars"] = df_agg["amount_cents"]/100.0

df_agg = df_agg.merge(accounts[["guid","parent_name","account_depth"]],left_on='expense_account_guid',right_on='guid',how='left')

df_agg["grouping"] = df_agg["grouping"] = df_agg["expense_category"].where(df_agg["account_depth"] == 1,df_agg["parent_name"])

app = dash.Dash(__name__)

fig = px.bar(df_agg, x="grouping", y="amount_dollars", color='expense_category', barmode="stack")
fig.update_layout(yaxis_tickformat='$,')

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
