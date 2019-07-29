
import pandas as pd
# import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime

import uuid
import json
import os
import boto3
import sys



from Scripts import utils
from Scripts import message_df_fx as msg_fx
from Scripts import usage_analysis_fx as usage
from Scripts import user_page_fx as user

# Settings
plt.ioff()
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TinderAnalysis')

class TinderTransform():

    def __init__(self, data_path):
        self.start_time = datetime.datetime.now()
        if not os.path.isfile(data_path):
            print("File not found at ", data_path)
        # Open JSON file
        with open(data_path, 'rb') as inp:
            self.data = json.load(inp)

    def execute(self):
        self.get_messages_df()
        self.get_message_plots()
        self.get_usage_df()
        self.get_user_df()
        self.combine_metrics()
        print("Choose export method")

    def get_messages_df(self):
        list_of_dfs = [msg_fx.get_msg_df(msg_dict) for msg_dict in self.data["Messages"]]
        self.all_msg_df = pd.concat(list_of_dfs, axis=0, sort=True)

    def get_message_plots(self):
        self.msg_plots = msg_fx.get_msg_related_plots(self.all_msg_df)
        self.msg_metrics = msg_fx.get_message_metrics(self.all_msg_df)

    def get_usage_df_plots(self):
        self.usage_df = pd.DataFrame(self.data["Usage"])
        self.usage_plots = usage.create_usage_plots(self.usage_df)
        self.usage_metrics = usage.gather_usage_stats(self.usage_df)

    def get_user_df(self):
        self.user_df = user.get_userdf_parts(self.data["User"])

    def combine_metrics(self):
        self.all_metrics = {}
        self.all_metrics["usage"] = self.usage_metrics
        self.all_metrics["message"] = self.msg_metrics
        self.all_metrics["user"] = self.user_df

        for metric_type in self.all_metrics.keys():
            if type(self.all_metrics[metric_type]) == dict:
                for key in self.all_metrics[metric_type].keys():
                    if (type(self.all_metrics[metric_type]) == pd.DataFrame) or \
                            (type(self.all_metrics[metric_type][key]) == pd.Series):
                        self.all_metrics[metric_type][key] = self.all_metrics[metric_type][key].to_dict()

    def export_plots_local(self, output_path):
        pp = PdfPages(output_path)
        for tmp_plt in self.msg_plots:
            pp.savefig(tmp_plt)

        for tmp_plt in self.usage_plots:
            pp.savefig(tmp_plt)

        pp.close()
        print("Completed parse json!")

    def upload_to_s3(self, bucket, output_path):
        self.unique_id = "_".join([self.all_metrics['user']['create_date'],
                              self.all_metrics['user']['birth_date']])

        new_key = 'graphs/output_graphs_' + self.unique_id + '.pdf'

        tbl_response = table.put_item(
            Item = {
                'created_birthday': self.unique_id,
                'request_date': str(datetime.datetime.now()),
                'pdf_s3_bucket': bucket,
                'pdf_s3_file_name': new_key,
                'user_df': self.all_metrics['user'],
                'usage_df': self.all_metrics['usage'],
                'message_df':self.all_metrics['message']
            }
        )
        s3_client.upload_file(output_path, bucket, new_key)

def handler(event, context):

    for record in event['Records']:
        uuid_key = uuid.uuid4()
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = str('/tmp/data_{}.json'.format(uuid_key))
        upload_path = str('/tmp/{}_output_graphs.pdf'.format(uuid_key))

        # Alternate data path
        data_path = "../Data/data.json"

        s3_client.download_file(bucket, key, download_path)
        pipeline = TinderTransform(download_path)
        pipeline.execute()
        pipeline.export_plots_local(upload_path)
        pipeline.upload_to_s3(bucket, upload_path)
        print("File stored at " + upload_path)


if __name__ =="__main__":
    input = sys.argv[1] # inputfile.txt
    with open(input, "rb") as inp:
        test_event = json.load(inp)
    handler(test_event, None)
    print("Completed python main fx")

