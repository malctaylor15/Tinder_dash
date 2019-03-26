
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import plotly.graph_objs as go
import pandas as pd
import json
from Scripts import message_df_fx as msg_fx
from Scripts import usage_analysis_fx as usage

import flask

# from flask import Blueprint, flash, g, redirect, render_template, request, url_for, Flask


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Open and parse file
data_path = "Data/data.json"
with open(data_path, "rb") as inp:
    data = json.load(inp)
list_of_dfs = [msg_fx.get_msg_df(msg_dict) for msg_dict in data["Messages"]]
all_msg_df = pd.concat(list_of_dfs, axis=0, sort=True)
all_msg_df['date'] = all_msg_df['sent_date'].dt.date

flag_col = ['explicit_word_in_msg', 'funny_word_in_msg', 'question_mark_in_msg', 'question_word_in_msg',
            "exclamation_mark_in_msg"]

def create_word_per_message_graph():
    dt_gb = all_msg_df.groupby('date')
    n_msg_over_time = dt_gb.apply(len)
    total_trace = go.Scatter(
        x=n_msg_over_time.index,
        y=n_msg_over_time.values,
        name="Total Number of Messages"
        )
    print(n_msg_over_time.shape)

    def create_plots(flag_over_time, flag_name):
        trace = go.Scatter(
            x=flag_over_time.index,
            y=flag_over_time,
            name= flag_name
        )
        return(trace)
    traces = [create_plots(dt_gb[flag].sum(), flag) for flag in flag_col]
    traces.insert(0, total_trace)

    layout = dict(title = 'Number of Message Types over Time',
                  xaxis = dict(title='Date'),
                  yaxis = dict(title='Number of Messages'),
                  plot_bgcolor = colors['background'],
                  paper_bgcolor = colors['background'],
                  font = {
                        'color': colors['text']
                  }
    )
    fig = go.Figure(data= traces, layout=layout)
    return(fig)

usage_df = pd.DataFrame(data["Usage"])


def create_max_usage_table():
    max_usage = usage.gather_max_usage(usage_df)
    trace_tbl = go.Table(header=dict(values=max_usage.columns,
                                     fill=dict(color=colors['background'])),
                         cells=dict(values=max_usage.values.T,
                                    fill=dict(color=colors['background'])),
                         name="Max Usage Metrics")
    data = [trace_tbl]
    layout=dict(  plot_bgcolor = colors['background'],
                  paper_bgcolor = colors['background'],
                  font = {
                        'color': colors['text'],
                        'size':14
                  })
    fig = go.Figure(data=data, layout=layout)
    return(fig)

def create_derived_metrics_table():
    derived_metrics = usage.gather_usage_stats(usage_df)
    derived_metrics = pd.Series(derived_metrics)
    trace_tbl = go.Table(header=dict(values=derived_metrics.index,
                                     fill=dict(color=colors['background'])),
                         cells=dict(values=derived_metrics.values,
                                    fill=dict(color=colors['background'])),
                         name="Derived Usage Metrics")
    data = [trace_tbl]
    layout = dict(plot_bgcolor = colors['background'],
                  paper_bgcolor = colors['background'],
                  font = {
                        'color': colors['text'],
                        'size':14
                  })
    fig = go.Figure(data=data, layout=layout)
    return(fig)



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
application = app.server

app.title = "Tinder Dashboard"


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Welcome To Malcolm\'s Tinder Data Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.H3(children='About Me', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    html.Div(children="""
    This website has various graphs and analysis about Malcolm's Tinder usage. 
    We look through the types of messages he sends and his usage of the apps. 
    
    This website is a work in progress and is an experiment in data analysis and deployment. 
    This site is made using the Dash framework and elastic beanstalk. 
    The analysis is mainly done in python. 
    """,
             style={
                'textAlign': 'center',
                'color': colors['text']
             }

             ),

    html.H2(children='Dashboards', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    dcc.Graph(
        id = 'Words per Message Graph',
        figure= create_word_per_message_graph()
    ),

    html.H2(children='Usage Analytics',
             style={
                'textAlign': 'center',
                'color': colors['text']
             }),

    html.Div(children = [
        html.H4(children='Max Usage Metrics',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
    ),
        dcc.Graph(
            id='Max Usage Table',
            figure=create_max_usage_table()
        )

    ]),

    html.Div(children=[
        html.H4(children='Dervied Usage Metrics',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }),
        dcc.Graph(
            id='Derived Usage Table',
            figure=create_derived_metrics_table()
        )
    ])

])


if __name__ == '__main__':
    # application.run(host="0.0.0.0")
    app.run_server(debug=True)