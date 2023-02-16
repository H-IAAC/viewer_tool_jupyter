import requests
import urllib.parse
import pandas as pd
from io import StringIO
import json
import csv
import os
from IPython.display import display, HTML
import shutil
from tqdm.auto import tqdm

class ViewerTool:    
    _url = "http://vm.hiaac.ic.unicamp.br:8081/"
    _api = "api/"
    
    def setup(self, url, port):
        self._url = url + ':' + port + '/'
    
    # 
    #    
    # @return DataFrame     Data from all stored experiments.
    def list_experiments(self):
        csv = self._request("list_all_experiments", "").text
        csvStringIO = StringIO(csv)
        df = pd.read_csv(csvStringIO)
        return df
    
    # 
    #    
    # @param string timestamp     formatted date to display
    # @param string priority      priority number
    # @param string priority_name priority name
    # @param string message       message to display
    #    
    # @return 
    def list_experiment_files(self, experiment, activity, user):
        query = {'experiment':experiment, 'activity':activity, 'user':user}
        data = self._request("list_experiment_files", query).json()
        
        if not data:
            print("No data found!")
            return None
        
        df = pd.DataFrame(data['files'], columns=["Files"])
        return df
    
    def get_csv(self, experiment, activity, user, filename, download=False):
        csv_url = self._format_as_download_url(experiment, activity, user, filename)

        if download:
            self.download_file(experiment, activity, user, filename, './Data/' + experiment + os.sep + user + os.sep + activity)
        
        try:
            df = pd.read_csv(csv_url, sep=';', skipinitialspace=True)
            df.Timestamp
        except AttributeError:
            df = pd.read_csv(csv_url, sep=',', skipinitialspace=True)
        except urllib.error.HTTPError as errh:
            print(f'Failed to download {filename}: {errh}')
            return None
            
        return df

    def get_video(self, experiment, activity, user, download=False):
        query = {'experiment':experiment, 'activity':activity, 'user':user}
        data = self._request("get_video_filename", query).json()
        
        filename = data["video"]
        
        if filename == 'none':
            return 'No video found.'
        
        video_url = self._format_as_download_url(experiment, activity, user, filename)

        if download:
            download_location = './Data/' + experiment + os.sep + user + os.sep + activity
            video_url = self.download_file(experiment, activity, user, filename, download_location)

        return video_url

    def display_video(self, experiment, activity, user, filename):
        video_url = self._format_as_download_url(experiment, activity, user, filename)
        video = HTML(f""" <video width="100%" height="300px" controls>
                         <source src={video_url} type="video/mp4">
                         </video>
                     """)
        return video

    def download_file(self, experiment, activity, user, filename, directory_location):
        
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
            # Code here will only run if the request is successful
        except requests.exceptions.HTTPError as errh:
            print(errh)
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        except requests.exceptions.Timeout as errt:
            print(errt)
        except requests.exceptions.RequestException as err:
            print(err)
    
        return response
