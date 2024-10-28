"""
Module to contain all the Prediction Models
"""

from pickle import load
from datetime import datetime

from sklearn.ensemble import (
    GradientBoostingRegressor,
)
from numpy import array, ndarray, zeros
from django.conf import settings


class DelayPredictor:
    """
    Class for the Delay Prediction Model
    """

    def __init__(self) -> None:
        """
        Class Initialization
        """
        self.time_series_offset = 5
        self.padding_value = 3.8676470588235294
        self.mean = array(
            [
                3.91867997,
                3.9132528,
                3.92008053,
                3.89565826,
                3.88103992,
                6.5,
                46.99387255,
                25.86519608,
            ]
        )
        self.var = array(
            [
                24.64748987,
                27.46465424,
                30.40886869,
                32.79536177,
                35.2247573,
                16.25,
                49.72667814,
                1.09947496,
            ]
        )
        self.areas = [
            "2nd Croos Kallady",
            "3rd Croos Kallady",
            "4th Croos Kallady - 1",
            "4th Croos Kallady - 2",
            "4th Croos Kallady - 3",
            "4th Croos Kallady - 4",
            "5th Croos Kallady ",
            "6th Croos Kallady ",
            "7th Croos Kallady ",
            "8th Croos Kallady ",
            "9th Croos Kallady ",
            "Babisingam Rd",
            "Babisingam Road",
            "Baugger mavadi Road",
            "Dharmasena Rd",
            "Dutch Bar Road",
            "Govt Quaters Rd",
            "Iqnasiyas Road",
            "Kallady 1st Cross",
            "Krishnankovil Road",
            "Malaimakal Road",
            "Mariyamman Kovil",
            "Music College",
            "New Dutchbar Rd",
            "New Kalmunai Road",
            "Old Kalmunai Road",
            "Pillayar Kovil Road",
            "Puvalapillai Road",
            "Sai Lane",
            "Saravana Rd",
            "Thiruchanthur",
            "Thiruchenthoor Beach road",
            "Thiruchenthu Road",
            "Thiruchenthur West",
            "Thirumakal Road",
            "Thomas Antony Road",
            "Varnakulasinam Road",
            "Velankerney Road",
        ]
        self.cell = ["Airtel", "Dialog", "Mobital"]
        self.agent = ["Jeya", "Sai", "Seera"]

    def get_model(self) -> GradientBoostingRegressor:
        """
        Function to load the Prediction Model
        """
        with open(f"{settings.BASE_DIR}//ml//grad_boost_model.pkl", "rb") as f:
            return load(f)

    def normalize(self, arr: ndarray, age: int, pay_date: int):
        """
        Normalize all the numerical features
        """
        return (
            array(list(arr) + [datetime.now().month] + [age, pay_date]) - self.mean
        ) / self.var

    def get_area_array(self, area_name: str):
        """
        Get One hot Encoder of Area
        """
        area_array = zeros(len(self.areas))
        if area_name in self.areas:
            area_array[self.areas.index(area_name)] = 1
        return area_array

    def get_agent_array(self, agent_name: str):
        """
        Get One hot Encoder of Agent
        """
        agent_array = zeros(len(self.agent))
        if agent_name in self.agent:
            agent_array[self.agent.index(agent_name)] = 1
        return agent_array

    def get_cell_career_array(self, number: str):
        """
        Get One hot Encoder of Cell Career
        """
        cell_array = zeros(len(self.cell))
        if number[2] in ["'6'", "7"]:
            cell_array[1] = 1
        elif number[2] in ["0", "1"]:
            cell_array[0] = 1
        else:
            cell_array[2] = 1
        return cell_array
