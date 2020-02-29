import pandas as pd
import numpy as np
import requests
import io

base_uri = "https://utilityapi.com/api/v2"


class UtilityAPIHandler:
    def __init__(self, cfg, meter_id, timezone, activation_time):

        self.meter_id        = meter_id
        self.token           = cfg.get("utilityapi", 'token')
        self.timezone        = timezone
        self.activation_time = activation_time

    def download_data(self, endpoint):
        uri = f"{base_uri}/{endpoint}?meters={self.meter_id}"
        header = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(uri, headers=header)
        return response.text

    def download_lineitems(self):
        line_item_response = self.download_data("files/meters_lineitems_csv")
        tmpdf = pd.read_csv(io.StringIO(line_item_response))

        return tmpdf

