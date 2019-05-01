import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import plotly.graph_objs as go
import pandas as pd
import TinderTransform
from Scripts import message_df_fx as msg_fx
from Scripts import usage_analysis_fx as usage


class TinderDash(TinderTransform):

    def __init__(self):

        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        self.app = dash.Dash()
        self.app.title = "Tinder Dashboard"
        self.colors = {
            'background': '#111111',
            'text': '#7FDBFF'
        }
        pass

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

    @self.app.callback(
        dd.Output(component_id='Words per Message Graph', component_property='figure'),
        [dd.Input(component_id='Words Per Message Frequency Radio Items', component_property='value')]
    )
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
