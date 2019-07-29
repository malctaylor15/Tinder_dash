import os
import io
import uuid
import base64
from flask_caching import Cache
import dash
import datetime
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dd
import plotly.graph_objs as go
import pandas as pd
import json
from Scripts import message_df_fx as msg_fx
from Scripts import usage_analysis_fx as usage



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

flag_col = ['explicit_word_in_msg', 'funny_word_in_msg', 'question_mark_in_msg', 'question_word_in_msg',
            "exclamation_mark_in_msg"]

# usage_df = pd.DataFrame(data["Usage"])
# usage_df.index = pd.to_datetime(usage_df.index)
# usage_df['total_swipes'] = usage_df['swipes_likes'] + usage_df['swipes_passes']
#
#


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

def serve_layout():
    session_id = str(uuid.uuid4())

    return(html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div([
        html.Div(children=session_id, id='session-id', style={'display': 'none'}),
        html.H1(
            children='Welcome To Malcolm\'s Tinder Data Dashboard',
            style=header_styles
        ),

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
        }
    ),
    html.Div(id='signal', style={'display': 'none'}),
    html.Div(id='upload-output', style = {'display' : 'none'}),
        html.Div(id='first_recall')
])
           )

app.layout = serve_layout()

@cache.memoize()
def get_main_dataframe(session_id, raw_upload):
    content_type, content_string = raw_upload.split(',')
    decoded = base64.b64decode(content_string)
    data = json.load(io.BytesIO(decoded))
    return(json.dumps(data))

def get_usage_dataframe(session_id, data):
    @cache.memoize()
    def calculate_usage_dataframe(session_id, data):
        usage_df = pd.DataFrame(data["Usage"])
        usage_df.index = pd.to_datetime(usage_df.index)
        usage_df['total_swipes'] = usage_df['swipes_likes'] + usage_df['swipes_passes']
        return(usage_df.reset_index().to_json())
    return(calculate_usage_dataframe(session_id, data))

def get_all_msg_dataframe(session_id, data):
    @ cache.memoize()
    def calculate_all_msg_dataframe(session_id, data):
        print('starting all msg 2')

        list_of_dfs = [msg_fx.get_msg_df(msg_dict) for msg_dict in data["Messages"]]
        print("Working on msg df "+ str(datetime.datetime.now()))
        all_msg_df = pd.concat(list_of_dfs, axis=0, sort=True)
        all_msg_df['date'] = all_msg_df['sent_date'].dt.date
        print('error in json')
        return(all_msg_df.reset_index().to_json())
    return(pd.read_json(calculate_all_msg_dataframe(session_id, data)))

@app.callback(dd.Output('upload-output', 'children'),
              [dd.Input('upload-data', 'contents', ),
               dd.Input('upload-data', 'filename'),
               dd.Input('session-id', 'children')])
def open_file(data, filename, session_id):
    if data is not None:
        content_type, content_string = data.split(',')
        if '.json' in filename:
            ret_val = base64.b64decode(content_string)
            data = json.load(io.BytesIO(ret_val))
        else:
            return(html.H1(children='File not a json'))

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

        try:
            print('starting all msg ')
            all_msg_df = get_all_msg_dataframe(session_id, data)
            print('finish all msg ')
            usage_df = get_usage_dataframe(session_id, data)
            out_string = "All msg df shape: " " Usage df shape: "
            print(out_string)
        except Exception as  e:
            print(e)
            out_string = str(len(data)) + " <- numb time ->"+ str(datetime.datetime.now())
        ret_val = html.Div([
            html.H1(children="Data was uploaded"),
            html.Div(id='raw_data', children=data)
        ])
        ret = html.H1(children=out_string)
        return(ret_val)

@app.callback(dd.Output('first_recall', 'children'),
              [dd.Input('upload-output', 'children'),
               dd.Input('session-id', 'children')])
def import_dataset(data, session_id):
    if data is not None:
        print('start next test')
        data = get_usage_dataframe(session_id, data)
        df = pd.read_json(data)
        nrow = str(df.shape[0])
        return(html.H1(children=nrow))
    else:
        return(html.H2(children="waiting for data upload"))

if __name__ == '__main__':
    # application.run(host="0.0.0.0")
    app.run_server(debug=True)
