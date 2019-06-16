
# -*- coding: utf-8 -*-
import os
import base64
import io
from flask_caching import Cache
import dash
import uuid
import datetime
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

# Flags used for message df
flag_col = ['explicit_word_in_msg', 'funny_word_in_msg', 'question_mark_in_msg', 'question_word_in_msg',
            "exclamation_mark_in_msg"]

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# # Open and parse file
# data_path = "Data/data.json"
# with open(data_path, "rb") as inp:
#     data = json.load(inp)
# list_of_dfs = [msg_fx.get_msg_df(msg_dict) for msg_dict in data["Messages"]]
# all_msg_df = pd.concat(list_of_dfs, axis=0, sort=True)
# all_msg_df['date'] = all_msg_df['sent_date'].dt.date
#
# flag_col = ['explicit_word_in_msg', 'funny_word_in_msg', 'question_mark_in_msg', 'question_word_in_msg',
#             "exclamation_mark_in_msg"]
#
# usage_df = pd.DataFrame(data["Usage"])
# usage_df.index = pd.to_datetime(usage_df.index)
# usage_df['total_swipes'] = usage_df['swipes_likes'] + usage_df['swipes_passes']




external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
CACHE_CONFIG = {
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 50  # should be equal to maximum number of active users
}
cache = Cache(app.server, config=CACHE_CONFIG)
about_me_container_props = {"style": {
                         'textAlign': 'center',
                         'color': colors['text']
                     }}

header_styles = {
            'textAlign': 'center',
            'color': colors['text']
        }

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
##############################################################################
#                                                                           #
#                                INTRODUCTION                               #
#                                                                           #
##############################################################################
    html.Div([
        html.H1(
            children='Welcome To Malcolm\'s Tinder Data Dashboard',
            style= header_styles
        ),
        html.H2(id='session_id', children=str(uuid.uuid4())),
        html.H3(children='About Me', style=header_styles),

        dcc.Markdown(children="""
        This website has various graphs and analysis about Malcolm's Tinder usage.   
        We look through the types of messages he sends and his usage of the apps.  
        This website is a work in progress and is an experiment in data analysis and deployment.  
        This site is made using the Dash framework and elastic beanstalk.  
        The analysis is mainly done in python.  
        """,
                 containerProps=about_me_container_props
                 )
    ]),

    dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
        multiple=True
        ),
    html.Div(id='usage_hidden', style={'display': 'none'}),
    html.Div(id='all_msg_hidden', style={'display': 'none'}),

##############################################################################
#                                                                           #
#                   WORDS PER MESSAGE GRAPHS                                #
#                                                                           #
##############################################################################
    html.Div(children=[
        html.H1(children = " Words Per Message Graphs",
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
        ),

        dcc.Markdown(children="""### About this Graph 
        
        The chart below shows the number of messages and messages with a certain words in the message sent to matches over time.
            * Funny words are ["hahaha", "lol", "haha", "ha", "hehe"]
         Types of messages:  
            * Question words are ["who", "what", "where", "when", "why", "how", "how's", "what's"]
            * Question mark implies there is a question mark in the message 
            * Exclaimation mark implies there is an exclaimation mark in the message
        
        """,
                     containerProps= about_me_container_props
         ),

        dcc.RadioItems(
            id='Words Per Message Frequency Radio Items',
            options=[
                {'label': 'Daily', 'value': 'D'},
                {'label': 'Weekly', 'value': 'W'},
                {'label': 'Monthly', 'value': 'M'},
            ],
            value='M',
            labelStyle={'display': 'inline-block'},
            style={'font': {
                            'color': colors['text']
                        }}),

        dcc.Graph(
            id='Words per Message Graph'
        )
    ]),
##############################################################################
#                                                                           #
#                   USAGE ANALYTICS GRAPHS/TABLES                           #
#                                                                           #
##############################################################################
    html.Div(children=[
        # Header
        html.Div([
            html.H1(children='Usage Analytics',
                     style=header_styles
                    ),
        ]),

        # Usage Plot
        html.Div(children=[
            html.H2(children="Usage Analytics Graph",
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }
            ),
            dcc.Markdown(children = """
            The chart below contains metrics of the user's usage over time. 
            Some of the metrics that are tracked are -- 
            app_opens refers to the number of times the user opened the application during the time period 
            swipe_likes refers to the number of times the user liked another user (swiping right) 
            swipe_passes refers to the number of times the user passed on another user (swiping left) 
            matches refers to the number of times the user and another user mutually liked each other during the specified time period
            messages_sent refers to the number of messages the user sent to other matches 
            messages_recieved refers to the number of messages the user recieved from matches 
            total_swipes is the total number of swipe_likes and swipe_passes 
            
            """,
                         containerProps=about_me_container_props),

            dcc.RadioItems(
                id='Usage Graph Frequency Radio Items',
                options=[
                    {'label': 'Daily', 'value': 'D'},
                    {'label': 'Weekly', 'value': 'W'},
                    {'label': 'Monthly', 'value': 'M'},
                ],
                value='M',
                labelStyle={'display': 'inline-block'},
                style=about_me_container_props

            ),
            dcc.Graph(
                id='Usage Graph'
            )
        ]),

        # Max Usage Table
        html.Div(children = [
            html.H4(children='Max Usage Metrics',
                    style=header_styles
                    ),
            dcc.Markdown(
               children=""" ### About Max Usage Table  
             THe first table  shows the date and number of max occurances of certain actions in interacting with the Tinder app. 
               
               """,
                containerProps = about_me_container_props
            ),
            dcc.Markdown(
                children="""### About Derived Usage Table  
   The second table shows several derived metrics about tinder usage given some of the other metrics.
   The date range selected is the same as the metrics table as above   
   The metrics are defined as 
        * Like to pass ratio: # Swipe rights (Like) / # Swipe Left (pass) 
            * Ratio > 1 indicates more likes than passes 
        * Swipes to app open: # Swipes / # Times Application Opened 
        * n_avg_msg_rec_per_match: # of messages **recieved** / # of matches 
            * Average conversation length from match POV 
        * n_avg_msg_sent_per_match: # of messages **sent**/ # of matches 
            * Average conversation length from your POV 
        * swipes_per_tot_cal_day: # total swipes / (Data obtained date - Tinder profile created) 
        * swipes_per_act_day : # total swipes / # of days app opened 
   """,
                containerProps=about_me_container_props
            ),

            dcc.DatePickerRange(
                id='Max Usage Metrics DatePickerRange',
                number_of_months_shown=6,
                style={'backgroundColor':colors['background']}
            ),
            dcc.Graph(
                id='Max Usage Table'
            ),
            html.H4(children='Dervied Usage Metrics',
                    style=header_styles),

            dcc.Graph(
                id='Derived Usage Table'
            )
        ])
    ])
])
# cache.init_app(app.server, config=CACHE_CONFIG)

# application = app.server

app.title = "Tinder Dashboard"


#############################################
#                                           #
############# FUNCTIONS #####################
#                                           #
#############################################

# @cache.memoize()
def open_usage_df(usage_json, session_id):
    print("parsing usage")
    usage_df = pd.DataFrame(usage_json)
    usage_df.index = pd.to_datetime(usage_df.index)
    usage_df['total_swipes'] = usage_df['swipes_likes'] + usage_df['swipes_passes']
    return(usage_df)

# @cache.memoize()
def open_all_msg_df(all_msg_json, session_id):
    print("parsing all msg")
    all_msg_df = pd.read_json(all_msg_json, orient='split')
    all_msg_df['sent_date'] = pd.to_datetime(all_msg_df['sent_date'])
    all_msg_df['date'] = all_msg_df['sent_date'].dt.date

    return(all_msg_df)


@app.callback([
                dd.Output('usage_hidden', 'children'),
                dd.Output('all_msg_hidden', 'children')
                ],
              [dd.Input('upload-data', 'contents'),
               dd.Input('upload-data', 'filename')])
def parse_upload(upload_file, filename):
    print('Parse upload function started')
    if upload_file is not None:
        print('Found uploaded file ')

        content_type, content_string = upload_file.split(',')
        # if '.json' in filename[-5:]:
        #     decoded = base64.b64decode(content_string)
        # elif '.zip' in filename[:-4]:
        #     # TODO: Add zip parsing logic
        #     pass
        decoded = base64.b64decode(content_string)
        data = json.load(io.BytesIO(decoded))
        list_of_dfs = [msg_fx.get_msg_df(msg_dict) for msg_dict in data["Messages"]]
        all_msg_df = pd.concat(list_of_dfs, axis=0, sort=True)
        # all_msg_df['date'] = all_msg_df['sent_date'].dt.date



        usage_df = pd.DataFrame(data["Usage"])
        # usage_df.index = pd.to_datetime(usage_df.index)
        usage_df['total_swipes'] = usage_df['swipes_likes'] + usage_df['swipes_passes']
        print('parse fx complete')
        return ([data['Usage']
            , all_msg_df.to_json(date_format='iso', orient='split')])
    else:
        print('Nothin uploaded, Time: ', str(datetime.datetime.now()))
        return([None, None])


@app.callback(
    dd.Output(component_id='Derived Usage Table', component_property='figure'),
    [dd.Input(component_id= 'usage_hidden', component_property='children'),
     dd.Input(component_id='Max Usage Metrics DatePickerRange', component_property='start_date'),
     dd.Input(component_id='Max Usage Metrics DatePickerRange', component_property='end_date')
     ])
def create_derived_metrics_table(usage_json, start_date, end_date):
    if usage_json is None:
        return(None)
    usage_df = open_usage_df(usage_json)
    filtered_usage = usage_df.loc[start_date:end_date]
    derived_metrics = usage.gather_usage_stats(filtered_usage)
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

@app.callback(
    [
        dd.Output('Max Usage Metrics DatePickerRange', 'min_date_allowed'),
        dd.Output('Max Usage Metrics DatePickerRange', 'max_date_allowed'),
        dd.Output('Max Usage Metrics DatePickerRange', 'start_date'),
        dd.Output('Max Usage Metrics DatePickerRange', 'end_date'),
    ],
    [dd.Input('usage_hidden', 'children')]
)
def define_datepicker(usage_json):
    if usage_json is None:
        return([None, None, None, None])
    usage_df = open_usage_df(usage_json)
    datepicker_specs = dict(min_date_allowed=usage_df.index.min().date(),
                max_date_allowed=usage_df.index.max().date(),
                start_date=usage_df.index.min().date(),
                end_date=usage_df.index.max().date())
    return(datepicker_specs)




@app.callback(
    dd.Output(component_id='Max Usage Table', component_property='figure'),
    [dd.Input(component_id= 'usage_hidden', component_property='children'),
    dd.Input(component_id= 'session_id', component_property='children'),
        dd.Input(component_id='Max Usage Metrics DatePickerRange', component_property='start_date'),
     dd.Input(component_id='Max Usage Metrics DatePickerRange', component_property='end_date')
     ])
def create_max_usage_table(usage_json, session_id, start_date, end_date):
    if usage_json is None:
        return()
    usage_df = open_usage_df(usage_json, session_id)
    filtered_usage = usage_df.loc[start_date:end_date]
    max_usage = usage.gather_max_usage(filtered_usage)

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


@app.callback(
    dd.Output(component_id='Words per Message Graph', component_property='figure'),
    [dd.Input(component_id='all_msg_hidden', component_property='children'),
     dd.Input(component_id='session_id', component_property='children'),
     dd.Input(component_id='Words Per Message Frequency Radio Items', component_property='value')]
)
def create_word_per_message_graph(all_msg_json, session_id, frequency):
    if all_msg_json is None:
        return()
    all_msg_df = open_all_msg_df(all_msg_json, session_id)
    all_msg_df.index = pd.to_datetime(all_msg_df['sent_date'])
    dt_gb = all_msg_df.groupby(pd.Grouper(freq=frequency))
    n_msg_over_time = dt_gb['message'].count()
    total_trace = go.Scatter(
        x=n_msg_over_time.index,
        y=n_msg_over_time.values,
        name="Total Number of Messages"
        )

    def create_plots(flag_over_time, flag_name):
        trace = go.Scatter(
            x=flag_over_time.index,
            y=flag_over_time,
            name= flag_name
        )
        return(trace)
    traces = [create_plots(dt_gb[flag].sum(), flag) for flag in flag_col]
    traces.insert(0, total_trace)

    layout = dict(title='Number of Message Types over Time',
                  xaxis=dict(title='Date'),
                  yaxis=dict(title='Number of Messages'),
                  plot_bgcolor=colors['background'],
                  paper_bgcolor=colors['background'],
                  font={
                        'color': colors['text']
                  }
    )
    fig = go.Figure(data=traces, layout=layout)
    return(fig)

@app.callback(
    dd.Output(component_id='Usage Graph', component_property='figure'),
    [dd.Input(component_id='usage_hidden', component_property='children'),
     dd.Input(component_id='session_id', component_property='children'),
     dd.Input(component_id='Usage Graph Frequency Radio Items', component_property='value')]
)
def create_usage_graph(usage_json, session_id, frequency):
    if usage_json is None:
        return()
    usage_df = open_usage_df(usage_json)
    dt_gb = usage_df.groupby(pd.Grouper(freq=frequency))

    def create_plots(flag_over_time, flag_name):
        trace = go.Scatter(
            x=flag_over_time.index,
            y=flag_over_time,
            name= flag_name
        )
        return(trace)
    traces = [create_plots(dt_gb[flag].sum(), flag) for flag in usage_df.columns]

    layout = dict(title = 'App Usage Over Time',
                  xaxis = dict(title='Date'),
                  yaxis = dict(title='Sum of Usage Metric'),
                  plot_bgcolor=colors['background'],
                  paper_bgcolor=colors['background'],
                  font={
                        'color': colors['text']
                  }
    )
    fig = go.Figure(data=traces, layout=layout)
    print("Re run at ", str(datetime.datetime.now()))
    return(fig)




if __name__ == '__main__':
    # application.run(host="0.0.0.0")
    app.run_server(debug=True, )
