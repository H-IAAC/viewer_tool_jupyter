import os
import json
import shutil
import requests
import urllib
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
    _head = {'Cookie': ''}

    def setup(self, url, port):
        self._url = url + ':' + port + '/'

    # Authentication
    #
    # @param string password  Password as string.
    #
    # @return string     True if success, otherwise False.
    def auth(self, password):
        url = self._url + 'in'

        query = { 'password' : password }
        data = requests.post(url, json = query)

        if data.text == 'OK':
            token = data.headers['set-cookie']
            self._head = {'Cookie': token}
            return True

        print(data.text)
        return False


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
    def list_experiment_files(self, experiment, activity, user, only_post_processor=False):
        query = {'experiment':experiment, 'activity':activity, 'user':user, 'only_post_processor':only_post_processor}
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
    def get_csv(self, experiment, activity, user, filename):
        csv_url = self._format_as_download_url(experiment, activity, user, filename)

        if not csv_url:
            return False

        download_location = './Data/' + experiment + os.sep + user + os.sep + activity
        csv_path = self._download_file(experiment, activity, user, filename, download_location)
        if not csv_path:
            return None
        return self._load_csv(csv_path)

    # Load CSV to DataFrame.
    #
    # @param csv csv_content  CSV as string.
    #
    # @return DataFrame     Data with CSV content.
    def _load_csv(self, csv_content):
        try:
            df = pd.read_csv(filepath_or_buffer=csv_content, sep=';', skipinitialspace=True)
            df.Timestamp
        except AttributeError:
            df = pd.read_csv(filepath_or_buffer=csv_content, sep=',', skipinitialspace=True)
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
        video_path = self.get_video(experiment, activity, user, True)

        video = HTML(f""" <video width="100%" height="300px" controls>
                         <source src={video_path} type="video/mp4">
                         </video>
                     """)
        return video


    def _download_file(self, experiment, activity, user, filename, directory_location):
        file_destination = directory_location + os.sep + filename
        file_url = self._format_as_download_url(experiment, activity, user, filename)

        if not file_url:
            return False

        # If file is already locally stored
        if os.path.isfile(file_destination):
            # then check if it has the same size from remote file
            file_size = self._get_content_size(file_url)
            current_file_size = int(os.stat(file_destination).st_size)
            if current_file_size == file_size:
                # if same size, then return the path to local file
                return file_destination

        # make an HTTP request within a context manager
        try:
            with requests.get(file_url, stream=True, headers=self._head) as r:
                r.raise_for_status()

                # check header to get content length, in bytes
                total_length = int(r.headers.get("Content-Length"))

                print(f'Saving {filename} to {file_destination}')

                # implement progress bar via tqdm
                with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
                    # Create directory_location
                    os.makedirs(directory_location, exist_ok=True)

                    with open(f"{file_destination}", 'wb') as output:
                        shutil.copyfileobj(raw, output)

        except requests.exceptions.HTTPError as errh:
            print('File not found!')

        return file_destination


    def _format_as_download_url(self, experiment, activity, user, filename):
        params = urllib.parse.quote('pre/' + experiment + ' [' + activity + '] [' + user + ']/' + filename)
        status_code = self._check_url(params)
        if status_code == 200:
            return self._url + params

        params = urllib.parse.quote('pos/' + experiment + ' [' + activity + '] [' + user + ']/' + filename)
        status_code = self._check_url(params)
        if status_code == 200:
            return self._url + params

        print("Invalid parameters/Unauthorized access")
        return False

    def _check_url(self, params):
        response = requests.head(self._url + params, headers=self._head)
        return response.status_code


    def _get_content_size(self, url):
        try:
            with requests.get(url, stream=True, headers=self._head) as r:
                r.raise_for_status()

                # check header to get content length, in bytes
                total_length = int(r.headers.get("Content-Length"))
                return total_length

        except requests.exceptions.HTTPError as errh:
            print('File not found!')

        return 0


    def _request(self, endpoint, query):
        try:
            response = requests.get(self._url + self._api + endpoint, params=query, timeout=5, headers=self._head)
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
