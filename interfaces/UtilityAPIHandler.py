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
        if not response.status_code == 200:
            msg = "Failed to fetch billing data. UtilityAPI Response:\n"
            msg += response.text
            raise ConnectionError(msg)

        return response.text

    def download_line_items(self):
        line_item_response = self.download_data("files/meters_lineitems_csv")
        tmpdf = pd.read_csv(io.StringIO(line_item_response),
                            parse_dates=["bill_start_date", "bill_end_date"])
        tmpdf.bill_start_date = tmpdf.bill_start_date.dt.tz_localize(self.timezone)
        tmpdf.bill_end_date = tmpdf.bill_end_date.dt.tz_localize(self.timezone)

        return tmpdf.query("bill_start_date >= @self.activation_time")

