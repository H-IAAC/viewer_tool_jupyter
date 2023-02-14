import requests
import urllib.parse
import pandas as pd
from io import StringIO
import json
import os
from IPython.display import display, HTML, IFrame

class ViewerTool:    
    _url = "http://vm.hiaac.ic.unicamp.br:8081/"
    #_url = "http://localhost:8080/"
    _api = "api/"
    
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
        df = pd.DataFrame(data['files'], columns=["Files"])
        return df
    
    def get_csv(self, experiment, activity, user, filename):
        csv_url = self._format_as_download_url(experiment, activity, user, filename)
        df = pd.read_csv(csv_url, sep=',', skipinitialspace=True)
        return df

    def display_video(self, experiment, activity, user, filename):
        video_url = self._format_as_download_url(experiment, activity, user, filename)
        video = HTML(f""" <video width="100%" height="300px" controls>
                         <source src={video_url} type="video/mp4">
                         </video>
                     """)
        return video
    def get_url_video(self, experiment, activity, user, filename):
        video_url = self._format_as_download_url(experiment, activity, user, filename)        
        return video_url

    def download_file(self, experiment, activity, user, filename, directory_location):
        file_url = self._format_as_download_url(experiment, activity, user, filename)
        result = requests.get(file_url, timeout=5)
        directory_location += os.sep + filename
        open(directory_location, 'wb').write(result.content)
        print(f'Saving {filename} as {directory_location}')
    
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
