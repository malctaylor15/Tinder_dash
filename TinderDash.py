import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import plotly.graph_objs as go
import pandas as pd
from TinderTransform import TinderTransform
from Scripts import message_df_fx as msg_fx
from Scripts import usage_analysis_fx as usage


class TinderDash(TinderTransform):

    def __init__(self, data_path):

        super(TinderDash, self).__init__(data_path)
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = dash.Dash()
        self.app.title = "Tinder Dashboard"
        self.colors = {
            'background': '#111111',
            'text': '#7FDBFF'
        }
        self.header_styles = {
            'textAlign': 'center',
            'color': self.colors['text']
        }
        self.about_me_container_props = {"style": {
                         'textAlign': 'center',
                         'color': self.colors['text']
                     }}

    def create_max_usage_table(self):
        max_usage = usage.gather_max_usage(self.usage_df)
        trace_tbl = go.Table(header=dict(values=max_usage.columns,
                                         fill=dict(color=self.colors['background'])),
                             cells=dict(values=max_usage.values.T,
                                        fill=dict(color=self.colors['background'])),
                             name="Max Usage Metrics")
        data = [trace_tbl]
        layout = dict(plot_bgcolor=self.colors['background'],
                      paper_bgcolor=self.colors['background'],
                      font={
                          'color': self.colors['text'],
                          'size': 14
                      })
        fig = go.Figure(data=data, layout=layout)
        return (fig)

    def create_derived_metrics_table(self):
        derived_metrics = usage.gather_usage_stats(self.usage_df)
        derived_metrics = pd.Series(derived_metrics)
        trace_tbl = go.Table(header=dict(values=derived_metrics.index,
                                         fill=dict(color=self.colors['background'])),
                             cells=dict(values=derived_metrics.values,
                                        fill=dict(color=self.colors['background'])),
                             name="Derived Usage Metrics")
        data = [trace_tbl]
        layout = dict(plot_bgcolor = self.colors['background'],
                      paper_bgcolor = self.colors['background'],
                      font = {
                            'color': self.colors['text'],
                            'size':14
                      })
        fig = go.Figure(data=data, layout=layout)
        return(fig)

    def create_word_per_message_graph(self, frequency):
        self.all_msg_df.index = pd.to_datetime(self.all_msg_df['sent_date'])
        dt_gb = self.all_msg_df.groupby(pd.Grouper(freq=frequency))
        n_msg_over_time = dt_gb['message'].count()
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
                name=flag_name
            )
            return (trace)

        flag_col = ['explicit_word_in_msg', 'funny_word_in_msg', 'question_mark_in_msg', 'question_word_in_msg',
                    "exclamation_mark_in_msg"]
        traces = [create_plots(dt_gb[flag].sum(), flag) for flag in flag_col]
        traces.insert(0, total_trace)

        layout = dict(title='Number of Message Types over Time',
                      xaxis=dict(title='Date'),
                      yaxis=dict(title='Number of Messages'),
                      plot_bgcolor=self.colors['background'],
                      paper_bgcolor=self.colors['background'],
                      font={
                          'color': self.colors['text']
                      }
                      )
        fig = go.Figure(data=traces, layout=layout)
        return (fig)

    def fill_in_site(self):

        self.app.layout = html.Div(style={'backgroundColor': self.colors['background']}, children=[
    ##############################################################################
    #                                                                           #
    #                                INTRODUCTION                               #
    #                                                                           #
    ##############################################################################
    html.Div([
        html.H1(
            children='Welcome To Malcolm\'s Tinder Data Dashboard',
            style=self.header_styles
        ),

        html.H3(children='About Me', style=self.header_styles),

        dcc.Markdown(children="""
        This website has various graphs and analysis about Malcolm's Tinder usage.   
        We look through the types of messages he sends and his usage of the apps.  
        This website is a work in progress and is an experiment in data analysis and deployment.  
        This site is made using the Dash framework and elastic beanstalk.  
        The analysis is mainly done in python.  
        """,
                     containerProps=self.about_me_container_props
                     ),

        html.H2(children='Dashboards', style=self.header_styles),
    ]),
    ##############################################################################
    #                                                                           #
    #                   WORDS PER MESSAGE GRAPHS                                #
    #                                                                           #
    ##############################################################################
    html.Div(children=[
        html.H2(children=" Words Per Message Graphs",
                style={
                    'textAlign': 'center',
                    'color': self.colors['text']
                }
                ),

        dcc.Markdown(children="""### About this Graph 

        The chart below shows the number of messages and messages with a certain words in the message sent to matches over time.
         Types of messages:  
            * Explicit words are ["fuck", "fucking", "fucked", "shit", "bitch", "sex", "ass", "shitty", "motherfucker"]
            * Funny words are ["hahaha", "lol", "haha", "ha", "hehe"]
            * Qeustion words are ["who", "what", "where", "when", "why", "how", "how's", "what's"]
            * Question mark implies there is a question mark in the message 
            * Exclaimation mark implies there is an exclaimation mark in the message

        """,
                     containerProps=self.about_me_container_props
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
            style=self.about_me_container_props

        ),

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
            html.H2(children='Usage Analytics',
                    style=self.header_styles
                    ),

        ]),

        # Max Usage Table
        html.Div(children=[
            html.H4(children='Max Usage Metrics',
                    style=self.header_styles
                    ),
            dcc.Markdown(
                children=""" ### About Max Usage Table  
             This table shows the date and number of max occurances of certain actions in interacting with the Tinder app. 

               """,
                containerProps=self.about_me_container_props
            ),
            dcc.Graph(
                id='Max Usage Table',
                figure=self.create_max_usage_table()
            )

        ]),
        # Other Metrics Table
        html.Div(children=[
            html.H4(children='Dervied Usage Metrics',
                    style=self.header_styles),

            dcc.Markdown(
                children="""### About Derived Usage Table  
           This table shows several derived metrics about tinder usage given some of the other metrics. 
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
                containerProps=self.about_me_container_props
            ),
            dcc.Graph(
                id='Derived Usage Table',
                figure=self.create_derived_metrics_table()
            )
        ])
    ])
])
