from typing import Dict, List, Any
from transformers import pipeline
import holidays
import datetime

class EndpointHandler():
    def __init__(self, path=""):
        # load the model
        self.pipeline = pipeline("text-classification", model=path)
        # initialize holidays for US
        self.holidays = holidays.US()

    def __call__(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        data args:
            inputs (:obj: `str`)
            date (:obj: `str`)
        Return:
            A :obj:`list` | `dict`: will be serialized and returned
        """
        # get inputs
        inputs = data.pop("inputs", data)
        # check for date in data, logic as per request
        date_str = data.pop("date", None)

        # check if date exists and if it is a holiday
        if date_str is not None:
            # simple check if the date string matches a holiday key
            # holidays library supports 'YYYY-MM-DD' strings lookup
            if date_str in self.holidays:
                 return [{"label": "happy", "score": 1}]

        # run normal prediction
        prediction = self.pipeline(inputs)
        return prediction
