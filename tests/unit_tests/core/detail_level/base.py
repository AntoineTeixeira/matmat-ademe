import os

import pandas as pd

from matmat.utils import constants as cst

class TestDetailLevel:

    dl_file = cst.DL_FILE
    dl_path = os.path.dirname(__file__)
    dl_file_path = os.path.join(dl_path, dl_file)

    # Sectors
    sectors_categories = ["C1", "C1", "C2", "C2", "C2", "C3"]
    sectors_sub_categories = ["SC11", "SC11", "SC21", "SC22", "SC22", "SC3"]
    sectors = ["S11", "S12", "S21", "S22", "S23", "S31"]
    dl_sectors = pd.DataFrame(
        {
            "category": sectors_categories,
            "sub_category": sectors_sub_categories,
            "sector": sectors,
        }
    )

    # Regions
    origins = ["domestic", "import", "import", "import"]
    regions = ["France", "Austria", "Slovakia", "Portugal"]
    dl_regions = pd.DataFrame(
        {
            "origin": origins,
            "region": regions,
        }
    )

    # Final demand
    fd_categories = [
        "Households",
        "Households",
        "Households",
        "Government",
        "Investment",
        "Exports",
    ]
    fd_sub_categories = ["Residential", "Transports", "Other", "G", "I", "E"]
    dl_final_demand = pd.DataFrame(
        {
            "Y_category": fd_categories,
            "Y_sub_category": fd_sub_categories,
        }
    )

    # Extensions
    dl_raw_materials = pd.DataFrame(
        {
            "category": sectors_categories,
            "sub_category": sectors_sub_categories,
            "sectors": sectors,
        }
    )
    ghg_emission_categories = ["CH4", "CO2", "NO2", "H2O"]
    dl_ghg_emissions = pd.DataFrame(
        {
            "category": ghg_emission_categories,
        }
    )

    @classmethod
    def setup_class(cls):

        with pd.ExcelWriter(cls.dl_file_path, engine="openpyxl") as writer:
            cls.dl_sectors.to_excel(writer, sheet_name="sectors", index=False)
            cls.dl_regions.to_excel(writer, sheet_name="regions", index=False)
            cls.dl_final_demand.to_excel(
                writer, sheet_name="final_demand_categories", index=False
            )
            cls.dl_raw_materials.to_excel(
                writer, sheet_name="raw_materials", index=False
            )
            cls.dl_ghg_emissions.to_excel(
                writer, sheet_name="ghg_emissions", index=False
            )

    @classmethod
    def teardown_class(cls):
        try:
            os.remove(cls.dl_file_path)
        except FileNotFoundError:
            pass
