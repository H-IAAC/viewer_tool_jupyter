import os
import json
import shutil
import requests
import urllib.parse
import pandas as pd

from io import StringIO
from IPython.display import display, HTML
from tqdm.notebook import tqdm

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime



class ViewerTool:
    _url = "http://vm.hiaac.ic.unicamp.br:8081/"
    _api = "api/"

    def setup(self, url, port):
        self._url = url + ':' + port + '/'

    # List all experiments available.
    # 
    # @return DataFrame     Data from all experiments available.
    def list_experiments(self):
        csv = self._request("list_all_experiments", "").text
        csvStringIO = StringIO(csv)
        df = pd.read_csv(csvStringIO)
        return df


    # Get a list of files related to an experiment.
    # 
    # @param string experiment  Experiment name.
    # @param string activity    Activity name.
    # @param string user        User name.
    # 
    # @return DataFrame     Data from all files available in this experiment.
    def list_experiment_files(self, experiment, activity, user):
        query = {'experiment':experiment, 'activity':activity, 'user':user}
        data = self._request("list_experiment_files", query).json()

        if not data:
            print("No data found!")
            return None

        df = pd.DataFrame(data['files'], columns=["Files"])
        return df


    # Get CSV content.
    # 
    # @param string experiment  Experiment name.
    # @param string activity    Activity name.
    # @param string user        User name.
    # @param string filename    CSV filename.
    # @param boolean download   Optional flag, used to download CSV.
    # 
    # @return DataFrame     Data with CSV content.
    def get_csv(self, experiment, activity, user, filename, download=False):
        csv_url = self._format_as_download_url(experiment, activity, user, filename)

        if download:
            download_location = './Data/' + experiment + os.sep + user + os.sep + activity
            self._download_file(experiment, activity, user, filename, download_location)

        try:
            df = pd.read_csv(csv_url, sep=';', skipinitialspace=True)
            df.Timestamp
        except AttributeError:
            df = pd.read_csv(csv_url, sep=',', skipinitialspace=True)
        except urllib.error.HTTPError as errh:
            print(f'Failed to download {filename}: {errh}')
            return None

        return df


    # Get a reference to the experiment video.
    # 
    # @param string experiment  Experiment name.
    # @param string activity    Activity name.
    # @param string user        User name.
    # @param boolean download   Optional flag, used to download the video.
    # 
    # @return string     If downloaded, return path to the video, and if not downloaded
    #                    then return an url to the video.
    def get_video(self, experiment, activity, user, download=False):
        query = {'experiment':experiment, 'activity':activity, 'user':user}
        data = self._request("get_video_filename", query).json()

        filename = data["video"]

        if filename == 'none':
            return 'No video found.'

        video_url = self._format_as_download_url(experiment, activity, user, filename)

        if download:
            download_location = './Data/' + experiment + os.sep + user + os.sep + activity
            video_url = self._download_file(experiment, activity, user, filename, download_location)

        return video_url


    # Display video.
    # 
    # @param string experiment  Experiment name.
    # @param string activity    Activity name.
    # @param string user        User name.
    # 
    # @return string     HTML component to render the video.
    def display_video(self, experiment, activity, user):
        video_url = self.get_video(experiment, activity, user)

        video = HTML(f""" <video width="100%" height="300px" controls>
                         <source src={video_url} type="video/mp4">
                         </video>
                     """)
        return video


    def _download_file(self, experiment, activity, user, filename, directory_location):

        video_location = ''
        file_destination = directory_location + os.sep + filename

        if os.path.exists(file_destination):
            return file_destination

        file_url = self._format_as_download_url(experiment, activity, user, filename)

        # make an HTTP request within a context manager
        try:
            with requests.get(file_url, stream=True) as r:
                r.raise_for_status()

                # check header to get content length, in bytes
                total_length = int(r.headers.get("Content-Length"))

                print(f'Saving {filename} to {file_destination}')

                # implement progress bar via tqdm
                with tqdm.wrapattr(r.raw, "read", total=total_length, desc="")as raw:
                    # Create directory_location
                    os.makedirs(directory_location, exist_ok=True)

                    with open(f"{file_destination}", 'wb') as output:
                        shutil.copyfileobj(raw, output)

        except requests.exceptions.HTTPError as errh:
            print('File not found!')

        return file_destination


    def _format_as_download_url(self, experiment, activity, user, filename):
         params = urllib.parse.quote(experiment + ' [' + activity + '] [' + user + ']/' + filename)
         return self._url + params


    def _request(self, endpoint, query):
        try:
            response = requests.get(self._url + self._api + endpoint, params=query, timeout=5)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(errh)

        except requests.exceptions.ConnectionError as errc:
            print(errc)

        except requests.exceptions.Timeout as errt:
            print(errt)

        except requests.exceptions.RequestException as err:
            print(err)

        return response
    
    

    
    
    def get_chart(self,dataset,fig,row,file_name):
        #print(dataset['Value 1'])
        #dataset["Date"] = [datetime.datetime.fromtimestamp(x/1000) for x in dataset['VideoTimelapse']]
        
        fig.add_trace(go.Scatter(x=dataset['sec'], y=dataset['Value 1'],mode='lines',name=file_name +' X',legendgroup = row),row=row, col=1)
        fig.add_trace(go.Scatter(x=dataset['sec'], y=dataset['Value 2'],mode='lines',name=file_name +' Y',legendgroup = row),row=row, col=1)
        fig.add_trace(go.Scatter(x=dataset['sec'], y=dataset['Value 3'],mode='lines',name=file_name +' Z',legendgroup = row),row=row, col=1)
        return fig

    def add_line_change_activites(f,change_activies):
        for time_activity in change_activies:
            f.add_vline(x=time_activity,line_width=1, line_dash="dash", line_color="green")
        return f

    def create_figs(self, experiment, activity, user,files,start=-1,end=-1):   
        fig = make_subplots(rows=len(files), cols=1, shared_xaxes=True,subplot_titles=(files))        
        try:
            
            row=0
            titles={}
            for file in files:
                df = self.get_csv(experiment, activity,user, file)
                df["sec"] =[x/1000 for x in df['VideoTimelapse']]
                if(start!=-1):
                    df = df[(df['sec'] >start)]
                if(end!=-1):
                    df = df[(df['sec'] <end)]                

                row=row+1
                self.get_chart(df,fig,row,file)

            fig.update_layout(
                        width=800,
                        height=len(files)*300,
                    title_text=experiment + ' '+user+' '+activity,
                    #hovermode= 'closest',
                    hovermode='x unified'
                #'xaxis': {'showspikes': True}
                    ) 
        except:
            print('erro')


        return fig
