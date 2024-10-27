from sklearn.ensemble import (
    GradientBoostingRegressor,
)
from numpy import array
from pickle import load
from django.conf import settings


class DelayPredictor:

    def __init__(self) -> None:
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
        with open(f"{settings.BASE_DIR}//ML//grad_boost_model.pkl", "rb") as f:
            return load(f)



