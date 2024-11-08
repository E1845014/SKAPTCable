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
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler


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


class Default_Predictor:
    """
    Class for the Default Prediction Model
    """

    def __init__(self):
        """
        Initialize Predictor
        """
        self.area_prob = {
            "2nd Croos Kallady": 1.000000,
            "3rd Croos Kallady": 0.933333,
            "4th Croos Kallady - 1": 1.000000,
            "4th Croos Kallady - 2": 1.000000,
            "4th Croos Kallady - 3": 1.000000,
            "4th Croos Kallady - 4": 1.000000,
            "5th Croos Kallady": 1.000000,
            "6th Croos Kallady": 1.000000,
            "7th Croos Kallady": 1.000000,
            "8th Croos Kallady": 0.870968,
            "9th Croos Kallady": 1.000000,
            "Babisingam Rd": 1.000000,
            "Babisingam Road": 1.000000,
            "Baugger mavadi Road": 1.000000,
            "Dharmasena Rd": 1.000000,
            "Dutch Bar Road": 1.000000,
            "Govt Quaters Rd": 1.000000,
            "Iqnasiyas Road": 0.977778,
            "Kallady 1st Cross": 1.000000,
            "Krishnankovil Road": 0.941176,
            "Malaimakal Road": 1.000000,
            "Mariyamman Kovil": 0.979592,
            "Music College": 1.000000,
            "New Dutchbar Rd": 0.980769,
            "New Kalmunai Road": 0.970588,
            "Old Kalmunai Road": 0.941176,
            "Pillayar Kovil Road": 1.000000,
            "Puvalapillai Road": 1.000000,
            "Sai Lane": 0.800000,
            "Saravana Rd": 0.966667,
            "Thiruchanthur": 1.000000,
            "Thiruchenthoor Beach road": 0.818182,
            "Thiruchenthu Road": 1.000000,
            "Thiruchenthur West": 0.800000,
            "Thirumakal Road": 1.000000,
            "Thomas Antony Road": 1.000000,
            "Varnakulasinam Road": 1.000000,
            "Velankerney Road": 1.000000,
        }
        self.age_prob = {
            33: 0.000000,
            35: 0.941176,
            36: 1.000000,
            37: 1.000000,
            38: 0.978261,
            39: 0.979167,
            40: 0.934783,
            41: 0.981481,
            42: 0.972973,
            43: 0.956522,
            44: 0.960784,
            45: 0.975610,
            46: 0.923077,
            47: 0.976744,
            48: 0.967742,
            49: 1.000000,
            50: 0.979167,
            51: 1.000000,
            52: 1.000000,
            53: 1.000000,
            54: 1.000000,
            55: 1.000000,
            56: 1.000000,
            57: 1.000000,
            58: 1.000000,
            59: 1.000000,
        }
        self.gender_probs = {"Female": 0.953271, "Male": 0.982869}
        self.cell_career_probs = {
            "Airtel": 0.985646,
            "Dialog": 0.974952,
            "Mobital": 0.980769,
        }
        self.agent_probs = {"Jeya": 0.986784, "Sai": 0.994220, "Seera": 0.966184}
        self.box_probs = {"analog": 0.933962, "digital": 0.985027}

    def get_model(self) -> SVC:
        """
        Function to load the Prediction Model
        """
        with open(f"{settings.BASE_DIR}//ml//SVC.pkl", "rb") as f:
            return load(f)

    def get_preprocessor(self) -> StandardScaler:
        """
        Function to load the Standard Scaler
        """
        with open(f"{settings.BASE_DIR}//ml//standard_scaler.pkl", "rb") as f:
            return load(f)
