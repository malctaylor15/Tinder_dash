# -*- coding: utf-8 -*-
import os
import base64
import io
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

## Default Graph

default_usage_tbl_data = go.Table(header={
    'values': ['metric', 'date', 'max date of index'],
    'fill': {'color': colors['background']}
},
    cells={'values': [['app_opens', 'swipe likes', 'swipe passes', 'matches', 'messages sent', 'messages recieved'],
                      ['2017-03-06', '2015-09-26', '2016-06-12', '2015-09-25', '2015-09-25', '2015-09-25',
                       '2015-09-25'],
                      ['348', '153', '87', '10', '36', '26']],
           'fill': {'color': colors['background']}
           },
    name='Max Usage Metrics'
)

default_derived_tbl_data = go.Table(header={
    'values': ['total_swipes', 'like_to_pass_ratio', 'swipes/app_open', 'n_avg_msg_rec_per_match'
        , 'n_avg_msg_sent_per_match', 'swipes_per_tot_cal_day', 'swipes_per_act_day'],
    'fill': {'color': colors['background']}
},
    cells={'values': [16196, 3.73, 4.21, 3.13, 3.87, 11, 24.28],
           'fill': {'color': colors['background']}
           },
    name='Max Usage Metrics'
)

default_tbl_layout = dict(plot_bgcolor=colors['background'],
                          paper_bgcolor=colors['background'],
                          font={
                              'color': colors['text'],
                              'size': 14
                          })
default_usage_tbl = go.Figure(data=[default_usage_tbl_data], layout=default_tbl_layout)
default_derived_tbl = go.Figure(data=[default_derived_tbl_data], layout=default_tbl_layout)
default_graph = go.Figure({
    'data': [
        {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'scatter', 'name': 'SF'},
        {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'scatter', 'name': u'Montréal'},
    ],
    'layout': {
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background']
    }})

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

header_styles = {
    'textAlign': 'center',
    'color': colors['text']
}

regular_text_style = {
                         'textAlign': 'center',
                         'color':colors['text'],
                         'background-color': colors['background']
                     }

radio_button_styles = {'textAlign': 'center',
                       'color': colors['text']}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    ##############################################################################
    #                                                                           #
    #                                INTRODUCTION                               #
    #                                                                           #
    ##############################################################################
    html.Div([
        html.H1(
            children='Welcome To Malcolm\'s Tinder Data Dashboard',
            style=header_styles
        ),
        html.Div(id='session_id', children=str(uuid.uuid4()), style={'display': 'none'}),
        html.H1(children='About Me', style=header_styles),

        html.Div(children="""
            This website has various graphs and analysis about Malcolm's Tinder usage.   
            We look through the types of messages he sends and his usage of the apps.  
            This website is a work in progress and is an experiment in data analysis and deployment.  
            This site is made using the Dash framework and elastic beanstalk.  
            The analysis is mainly done in python.  

            Many of the charts are interactive. You can drag to zoom in on a certain part of the graph. 
            In the top right hand corner, there are additional tools to maneuver the image. 
            You can double click to return to original state. 

            """
                 , style=regular_text_style
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
            'margin': '10px',
            'color': colors['text']

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
        html.H1(children=" Words Per Message Graphs",
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
                ),
        html.Div([html.H2(children="About this Graph", style=header_styles),
                  dcc.Markdown(children=""" 
            The chart below shows the number of messages and messages with a certain words in the message sent to matches over time.   
            - Funny words are "hahaha", "lol", "haha", "ha", "hehe"  
            Types of messages:  
            - Question words are "who", "what", "where", "when", "why", "how", "how's", "what's"  
            - Question mark implies there is a question mark in the message  
            - Exclaimation mark implies there is an exclaimation mark in the message   

            Use the radio buttons below to select the frequency of the analysis
            """
                               , style=regular_text_style
                               )],
                 style=regular_text_style
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
            style=radio_button_styles),

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
            dcc.Markdown(children="""
            The chart below contains metrics of the user's usage over time. 
            Some of the metrics that are tracked are -- 
            - app_opens refers to the number of times the user opened the application during the time period 
            - swipe_likes refers to the number of times the user liked another user (swiping right) 
            - swipe_passes refers to the number of times the user passed on another user (swiping left) 
            - matches refers to the number of times the user and another user mutually liked each other during the specified time period
            - messages_sent refers to the number of messages the user sent to other matches 
            - messages_recieved refers to the number of messages the user recieved from matches 
            - total_swipes is the total number of swipe_likes and swipe_passes 

            """,
                         style=regular_text_style),

            dcc.RadioItems(
                id='Usage Graph Frequency Radio Items',
                options=[
                    {'label': 'Daily', 'value': 'D'},
                    {'label': 'Weekly', 'value': 'W'},
                    {'label': 'Monthly', 'value': 'M'},
                ],
                value='M',
                labelStyle={'display': 'inline-block'},
                style=radio_button_styles

            ),
            dcc.Graph(
                id='Usage Graph'
            )
        ]),

        # Max Usage Table
        html.Div(children=[
            html.H1(children='Max Usage Metrics',
                    style=header_styles
                    ),
            html.H2(
                children="About Max Usage Table "
                , style=header_styles
            ),
            html.Div(children="""             
             The first table  shows the date and number of max occurances of certain actions in interacting with the Tinder app. 
             There is a short description of each of the metrics before the table is presented.    
             The second table has a few custom metrics and ratios about your usage.   

             Use the time filter below to select the range of dates of interest. The time filter applies to both tables. 


               """,
                     style=regular_text_style
                     ),
            dcc.DatePickerRange(
                id='Max Usage Metrics DatePickerRange',
                number_of_months_shown=6,
                style=radio_button_styles
            ),
            html.H3("About Derived Usage Table",
                    style=header_styles),

            dcc.Markdown(
                children=""" 
 The second table shows several derived metrics about tinder usage given some of the other metrics.
 The date range selected is the same as the metrics table as above   
 The metrics are defined as :   
 - Like to pass ratio: # Swipe rights (Like) / # Swipe Left (pass)  
 - Ratio > 1 indicates more likes than passes  
 - Swipes to app open: # Swipes / # Times Application Opened  
 - n_avg_msg_rec_per_match: # of messages **recieved** / # of matches  
 - Average conversation length from match POV  
 - n_avg_msg_sent_per_match: # of messages **sent**/ # of matches  
 - Average conversation length from your POV   
 - swipes_per_tot_cal_day: # total swipes / (Data obtained date - Tinder profile created)   
 - swipes_per_act_day : # total swipes / # of days app opened 
 """,
                style=regular_text_style
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

# application = app.server

app.title = "Tinder Dashboard"


#############################################
#                                           #
############# FUNCTIONS #####################
#                                           #
#############################################

def open_usage_df(usage_json_string, session_id):
    print("parsing usage")
    # TODO: Think about this string -> json -> Dataframe conversion and simplify
    usage_json = json.loads(usage_json_string)
    usage_df = pd.DataFrame(usage_json)
    usage_df.index = pd.to_datetime(usage_df.index)
    # usage_df['total_swipes'] = usage_df['swipes_likes'] + usage_df['swipes_passes']
    return (usage_df)


def open_all_msg_df(all_msg_json, session_id):
    print("parsing all msg")
    all_msg_df = pd.read_json(all_msg_json, orient='split')
    all_msg_df.set_index(['match_id', 'msg_number'], inplace=True)
    all_msg_df['sent_date'] = pd.to_datetime(all_msg_df['sent_date'])
    all_msg_df['date'] = all_msg_df['sent_date'].dt.date

    return (all_msg_df)


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
        content_type, content_string = upload_file[0].split(',')
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
        msg_df_string = all_msg_df.reset_index().to_json(date_format='iso', orient='split')
        usage_df_string = json.dumps(data['Usage'])
        print('parse fx complete')
        return ([usage_df_string, msg_df_string])
    else:
        print('Nothin uploaded, Time: ', str(datetime.datetime.now()))
        return ([None, None])


@app.callback(
    dd.Output(component_id='Derived Usage Table', component_property='figure'),
    [dd.Input(component_id='usage_hidden', component_property='children'),
     dd.Input(component_id='Max Usage Metrics DatePickerRange', component_property='start_date'),
     dd.Input(component_id='Max Usage Metrics DatePickerRange', component_property='end_date'),
     dd.Input(component_id='session_id', component_property='children')
     ])
def create_derived_metrics_table(usage_json, start_date, end_date, session_id):
    if usage_json is None:
        return (default_derived_tbl)
    usage_df = open_usage_df(usage_json, session_id)
    filtered_usage = usage_df.loc[start_date:end_date]
    derived_metrics = usage.gather_usage_stats(filtered_usage)
    derived_metrics = pd.Series(derived_metrics)
    trace_tbl = go.Table(header=dict(values=derived_metrics.index,
                                     fill=dict(color=colors['background'])),
                         cells=dict(values=derived_metrics.values,
                                    fill=dict(color=colors['background'])),
                         name="Derived Usage Metrics")
    data = [trace_tbl]
    layout = dict(plot_bgcolor=colors['background'],
                  paper_bgcolor=colors['background'],
                  font={
                      'color': colors['text'],
                      'size': 14
                  })
    fig = go.Figure(data=data, layout=layout)
    return (fig)


@app.callback(
    [
        dd.Output('Max Usage Metrics DatePickerRange', 'min_date_allowed'),
        dd.Output('Max Usage Metrics DatePickerRange', 'max_date_allowed'),
        dd.Output('Max Usage Metrics DatePickerRange', 'start_date'),
        dd.Output('Max Usage Metrics DatePickerRange', 'end_date'),
        dd.Output('Max Usage Metrics DatePickerRange', 'initial_visible_month'),

    ],
    [dd.Input('usage_hidden', 'children'),
     dd.Input('session_id', 'children'),

     ]
)
def define_datepicker(usage_json, session_id):
    if usage_json is None:
        return ([None, None, None, None, None])
    usage_df = open_usage_df(usage_json, session_id)
    datepicker_specs = [usage_df.index.min().date(),
                        usage_df.index.max().date(),
                        usage_df.index.min().date(),
                        usage_df.index.max().date(),
                        usage_df.index.max().date()]
    return (datepicker_specs)


@app.callback(
    dd.Output(component_id='Max Usage Table', component_property='figure'),
    [dd.Input(component_id='usage_hidden', component_property='children'),
     dd.Input(component_id='session_id', component_property='children'),
     dd.Input(component_id='Max Usage Metrics DatePickerRange', component_property='start_date'),
     dd.Input(component_id='Max Usage Metrics DatePickerRange', component_property='end_date')
     ])
def create_max_usage_table(usage_json, session_id, start_date, end_date):
    if usage_json is None:
        return (default_usage_tbl)
    usage_df = open_usage_df(usage_json, session_id)
    filtered_usage = usage_df.loc[start_date:end_date]
    max_usage = usage.gather_max_usage(filtered_usage)

    trace_tbl = go.Table(header=dict(values=max_usage.columns,
                                     fill=dict(color=colors['background'])),
                         cells=dict(values=max_usage.values.T,
                                    fill=dict(color=colors['background'])),
                         name="Max Usage Metrics")
    data = [trace_tbl]
    layout = dict(plot_bgcolor=colors['background'],
                  paper_bgcolor=colors['background'],
                  font={
                      'color': colors['text'],
                      'size': 14
                  })
    fig = go.Figure(data=data, layout=layout)
    return (fig)


@app.callback(
    dd.Output(component_id='Words per Message Graph', component_property='figure'),
    [dd.Input(component_id='all_msg_hidden', component_property='children'),
     dd.Input(component_id='session_id', component_property='children'),
     dd.Input(component_id='Words Per Message Frequency Radio Items', component_property='value')]
)
def create_word_per_message_graph(all_msg_json, session_id, frequency):
    if all_msg_json is None:
        return (default_graph)
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
            name=flag_name
        )
        return (trace)

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
    return (fig)


@app.callback(
    dd.Output(component_id='Usage Graph', component_property='figure'),
    [dd.Input(component_id='usage_hidden', component_property='children'),
     dd.Input(component_id='session_id', component_property='children'),
     dd.Input(component_id='Usage Graph Frequency Radio Items', component_property='value')]
)
def create_usage_graph(usage_json, session_id, frequency):
    if usage_json is None:
        return (default_graph)
    usage_df = open_usage_df(usage_json, session_id)
    dt_gb = usage_df.groupby(pd.Grouper(freq=frequency))

    def create_plots(flag_over_time, flag_name):
        trace = go.Scatter(
            x=flag_over_time.index,
            y=flag_over_time,
            name=flag_name
        )
        return (trace)

    traces = [create_plots(dt_gb[flag].sum(), flag) for flag in usage_df.columns]

    layout = dict(title='App Usage Over Time',
                  xaxis=dict(title='Date'),
                  yaxis=dict(title='Sum of Usage Metric'),
                  plot_bgcolor=colors['background'],
                  paper_bgcolor=colors['background'],
                  font={
                      'color': colors['text']
                  }
                  )
    fig = go.Figure(data=traces, layout=layout)
    print("Re run at ", str(datetime.datetime.now()))
    return (fig)


if __name__ == '__main__':
    # application.run(host="0.0.0.0")
    app.run_server(debug=True, host="0.0.0.0" )