
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import plotly.graph_objs as go
import pandas as pd
import json
from Scripts import message_df_fx as msg_fx
import flask

# Open and parse file
data_path = "Data/data.json"
with open(data_path, "rb") as inp:
    data = json.load(inp)
list_of_dfs = [msg_fx.get_msg_df(msg_dict) for msg_dict in data["Messages"]]
all_msg_df = pd.concat(list_of_dfs, axis=0, sort=True)
all_msg_df['date'] = all_msg_df['sent_date'].dt.date

flag_col = ['explicit_word_in_msg', 'funny_word_in_msg', 'question_mark_in_msg', 'question_word_in_msg',
            "exclamation_mark_in_msg"]

server = flask.Flask(__name__)
# @app.callback(dd.Output(component_id = 'Words per Message Graph', component_property='figure'), [])
@server.route("/")
def create_word_per_message_graph():
    dt_gb = all_msg_df  .groupby('date')
    n_msg_over_time = dt_gb.apply(len)
    print(n_msg_over_time.shape)

    def create_plots(flag_over_time, flag_name):
        trace = go.Scatter(
            x=flag_over_time.index,
            y=flag_over_time,
            name= flag_name
        )
        return(trace)
    traces = [create_plots(dt_gb[flag].sum(), flag) for flag in flag_col]

    layout = dict(title = 'Word per Mesasge over Time',
                  xaxis = dict(title='Date'),
                  yaxis = dict(title='Word per Message'),
                  plot_bgcolor = colors['background'],
                  paper_bgcolor = colors['background'],
                    font = {
                        'color': colors['text']
                    }
                  )
    fig = go.Figure(data= traces, layout=layout)
    return(fig)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Tinder Dashboard"
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Welcome To Malcolm\'s Tinder Data Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='About Me', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    html.Div(children='Dashboards', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    dcc.Graph(
        id = 'Words per Message Graph',
        figure= create_word_per_message_graph()
    )
])



if __name__ == '__main__':
    app.run_server(server = server)