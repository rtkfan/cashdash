import config
import sqlite3
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import datetime

def get_data(path):
    con = sqlite3.connect(config.CONFIG_DB_LOCATION)
    with open(path) as f:
        query = f.read()
    df = pd.read_sql_query(query,con)
    con.close()
    return df

splits = get_data('./queries/get_expenses_by_payment_account.sql')
accounts = get_data('./queries/get_account_full_paths.sql')

earliest_tx = datetime.datetime.strptime(min(splits["post_date"]),'%Y-%m-%d %H:%M:%S').date()
latest_tx = datetime.datetime.strptime(max(splits["post_date"]),'%Y-%m-%d %H:%M:%S').date()

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Expenses'),

    html.Div(children='''
        Hello world, but for graphs.
    '''),

    dcc.Graph(
        id='example-income_statement'
    ),

    dcc.DatePickerRange(
        id='transaction-date-filter',
        min_date_allowed=earliest_tx,
        max_date_allowed=latest_tx,
        initial_visible_month=latest_tx,
        start_date=earliest_tx,
        end_date=latest_tx,
        display_format='YYYY-MM-DD'
    )
])


@app.callback(
    Output(component_id='example-income_statement', component_property='figure'),
    Input(component_id='transaction-date-filter', component_property = 'start_date'),
    Input(component_id='transaction-date-filter', component_property = 'end_date'),
)
def update_output(out_start, out_end):
    df_agg = splits[(splits["expense_type"]=='EXPENSE') &
                    (splits["post_date"]>=out_start) &
                    (splits["post_date"]<=out_end)].groupby(by=["expense_category","expense_account_guid"],
                                                       as_index=False)["amount_cents"].sum()
    df_agg.sort_values("amount_cents", inplace=True, ascending=False)
    df_agg["amount_dollars"] = df_agg["amount_cents"]/100.0
    df_agg = df_agg.merge(accounts[["guid","parent_name","account_depth"]],left_on='expense_account_guid',right_on='guid',how='left')
    df_agg["grouping"] = df_agg["grouping"] = df_agg["expense_category"].where(df_agg["account_depth"] == 1,df_agg["parent_name"])

    fig = px.bar(df_agg, x="grouping", y="amount_dollars", color='expense_category', barmode="stack")
    fig.update_layout(yaxis_tickformat='$,')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
