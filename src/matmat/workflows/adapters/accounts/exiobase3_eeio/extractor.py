"""
Overview
********
Extension Extraction Utilities: this module defines reusable classes for
extracting and transforming environmental extensions from an EXIOBASE MRIO
system using `pymrio`.

Core features
*************
- Generic `ExtensionExtractor` class for filtering and reindexing
- Specialized extractors for raw materials, labor, land use, water, GHGs, etc.
- Modular mapping and aggregation tools for categorical remapping

Contents
********
- ExtensionExtractor
- GreenhouseGasEmissionsExtractor
- RawMaterialsExtractor
- LabourExtractor
- ValueAddedExtractor
- WaterExtractor
- LandUseExtractor

# Todo: add to md file description on how to add new extension from exiobase.

"""

import copy

import pandas as pd
import numpy as np
import pymrio

import matmat.utils.constants as cst


class ExtensionExtractor:
    """
    Utility class for extracting sub-extensions from pymrio.Extension objects
    using a boolean index. Reusable for multiple environmental extensions.
    """
    VAR_LIST_NAMES = [cst.F_Z.split("_")[0], cst.F_Y, cst.UNIT]
    """The list of variable names to extract in each extension."""

    def __init__(self, extensions: pymrio.Extension):
        """
        Initialize the extractor with a given MRIO extension database.

        Parameters
        ----------
        extensions : pymrio.Extensions
            The loaded EXIOBASE IO extension.
        """
        self._extensions = extensions

    @staticmethod
    def extract_based_on_bool_index(
        index: pd.Series, extension_in: pymrio.Extension, extension_name: str
    ) -> pymrio.Extension:
        """
        Extract a new pymrio.Extension from an existing one using a boolean index.

        Parameters
        ----------
        index : pd.Series of bool
            Boolean mask applied on the stressor axis.
        extension_in : pymrio.Extension
            Source extension to extract data from.
        extension_name : str
            Name of the new extension.

        Returns
        -------
        pymrio.Extension
            Filtered extension containing only the selected stressors.
        """
        extension_out = pymrio.Extension(extension_name)

        for var in ExtensionExtractor.VAR_LIST_NAMES:
            # extract df from extension
            df = getattr(extension_in, var)

            # # Adapt index name for UNIT (unit tables often lack named index)
            # index_name = df.index.name if var != cst.UNIT else "index"

            # Apply filtering
            index_name = df.index.name
            df = df.reset_index().loc[index]
            df.set_index(index_name, inplace=True)
            setattr(extension_out, var, df)

        return extension_out

    @staticmethod
    def extract_by_unit_value(
        extension_in: pymrio.Extension, extension_name: str, target_unit: str
    ) -> pymrio.Extension:
        """
        Extract a pymrio.Extension based on a target unit value.

        Parameters
        ----------
        extension_in : pymrio.Extension
            Input extension to filter.
        extension_name : str
            Name of the new extension to create.
        target_unit : str
            Unit string to match (e.g., "km2" for land use).

        Returns
        -------
        pymrio.Extension
            Filtered extension containing only rows with the given unit.
        """
        # Build boolean index where unit equals the target unit
        unit_df = extension_in.unit.reset_index()
        is_target_unit = unit_df.iloc[:, 1] == target_unit

        return ExtensionExtractor.extract_based_on_bool_index(
            index=is_target_unit,
            extension_in=extension_in,
            extension_name=extension_name,
        )

    # ToDo: drop because depreciated? To do in workflow?
    @staticmethod
    def apply_index_mapping(
        extension: pymrio.Extension,
        mapping_dict: dict[str, list[str]],
        level_names: list[str],
    ) -> pymrio.Extension:
        """
        Apply a category/subcategory/sector mapping to the index of a pymrio.Extension.

        Parameters
        ----------
        extension : pymrio.Extension
            The extension whose index should be remapped.
        mapping_dict : dict
            Dictionary mapping high-level categories to subcategory names.
        level_names : list of str, optional
            Names for the resulting MultiIndex levels.

        Returns
        -------
        pymrio.Extension
            Extension with updated MultiIndex on all variables.
        """
        # Invert the mapping: subcategory → category
        inverse_map = {
            subcat: cat
            for cat, subcats in mapping_dict.items()
            for subcat in subcats
        }

        # get existing index
        index = extension.unit.index

        # Build new MultiIndex
        new_index = pd.MultiIndex.from_arrays(
            [
                index.get_level_values(0).map(inverse_map).values,
                index.get_level_values(0).values,
                index.get_level_values(1).values,
            ],
            names=level_names,
        )

        # Apply to all variables
        for var in ExtensionExtractor.VAR_LIST_NAMES:
            df = getattr(extension, var)
            df.index = new_index
            setattr(extension, var, df)

        return extension

    # ToDo: drop because depreciated? To do in workflow?
    @staticmethod
    def aggregate_by_top_level(
        extension: pymrio.Extension, level: str | int = cst.IDX_CATEGORY
    ) -> pymrio.Extension:
        """
        Aggregate a pymrio.Extension along its top-level index (e.g., category).

        Parameters
        ----------
        extension : pymrio.Extension
            Extension to aggregate.
        level : int, optional
            Index level to group by (default: 0).

        Returns
        -------
        pymrio.Extension
            Aggregated extension.
        """
        for attr in ExtensionExtractor.VAR_LIST_NAMES:
            df = getattr(extension, attr)
            df = df.groupby(level=level).sum()

            # Assume uniform units per aggregated group
            if attr == cst.UNIT:
                df.loc[:, :] = np.array(
                    [elt[0:2] for elt in df.squeeze().values.tolist()]
                ).reshape(-1, 1)

            setattr(extension, attr, df)

        return extension


class GreenhouseGasEmissionsExtractor(ExtensionExtractor):
    """
    Extract and process GHG emissions from a pymrio.IOSystem.

    This class separates GHG emissions into combustion-related and other sources,
    and converts all values into CO₂-equivalent (CO₂-eq) using global warming
    potential (GWP) multipliers defined in `cst.MULT_TO_CO2EQ`.

    Attributes
    ----------
    mrio : pymrio.IOSystem
        The input IO system containing environmental extensions.
    version : str
        The EXIOBASE version used (may influence where emissions are stored).
    """
    KEYS_GREENHOUSE_GAS = ["CO2", "CH4", "N2O", "SF6", "HFC", "PFC"]

    def extract(self)->pymrio.Extension:
        """
        Extract and return GHG emissions, split into combustion and other sources.

        Returns
        -------
        pymrio.Extension
            GHG emissions extension in MtCO2eq aggregated by gas and
            distinguishing emissions from combustion from other emissions
            categories.
        """
        ghg_emissions = self._extract_all_ghg_emissions()

        ghg_combustion = self._extract_ghg_emissions_from_combustion(ghg_emissions)
        ghg_other = self._extract_ghg_other(ghg_emissions, ghg_combustion)

        ghg_combustion = self._convert_to_co2eq(ghg_combustion)
        ghg_other = self._convert_to_co2eq(ghg_other)

        ghg_emissions = pymrio.Extension(
            name=cst.GHG_EMISSIONS,
            F=pd.concat(
                {
                    cst.GHG_COMBUSTION: ghg_combustion.F,
                    cst.GHG_OTHER: ghg_other.F,
                }
            ),
            unit=pd.concat(
                {
                    cst.GHG_COMBUSTION: ghg_combustion.unit,
                    cst.GHG_OTHER: ghg_other.unit,
                }
            ),
        )
        index_names = [cst.IDX_SOURCE, cst.IDX_GAS]
        ghg_emissions.F.index.names = index_names
        ghg_emissions.unit.index.names = index_names

        return ghg_emissions

    # ToDo: drop indicator
    def _extract_all_ghg_emissions(self) -> pymrio.Extension:
        """
        Extract all GHG emissions from the appropriate EXIOBASE extension.

        Returns
        -------
        pymrio.Extension
            Extension containing all GHG emissions.
        """
        extension_in = self._extensions.copy()
        stressors = extension_in.F.reset_index().indicator
        is_ghg = stressors.apply(
            lambda x: x.split(" ")[0] in self.KEYS_GREENHOUSE_GAS
        )
        ghg_emissions = self.extract_based_on_bool_index(
            is_ghg, extension_in, cst.GHG_EMISSIONS
        )

        return ghg_emissions

    # ToDo: drop indicator
    def _extract_ghg_emissions_from_combustion(
        self, ghg_extension: pymrio.Extension
    ) -> pymrio.Extension:
        """
        Extract GHG emissions from combustion-related activities.

        Parameters
        ----------
        ghg_extension : pymrio.Extension
            Extension containing all GHGs.

        Returns
        -------
        pymrio.Extension
            Extension containing only combustion-related GHGs.
        """
        stressors = ghg_extension.F.reset_index().indicator
        is_combustion = stressors.apply(
            lambda x: x.split(" - ")[1] == cst.GHG_COMBUSTION.split("_")[1]
        )
        combustion_ext = self.extract_based_on_bool_index(
            is_combustion, ghg_extension, cst.GHG_COMBUSTION
        )
        return combustion_ext

    def _extract_ghg_other(
        self, ghg_extension: pymrio.Extension, ghg_combustion: pymrio.Extension
    ) -> pymrio.Extension:
        """
        Extract GHG emissions not related to combustion.

        Parameters
        ----------
        ghg_extension : pymrio.Extension
            Full GHG extension.
        ghg_combustion : pymrio.Extension
            Combustion-related GHGs.

        Returns
        -------
        pymrio.Extension
            GHGs from other sources, in CO₂-eq.
        """
        extension = pymrio.Extension(cst.GHG_OTHER)

        for attr in self.VAR_LIST_NAMES:
            df_all = getattr(ghg_extension, attr)
            df_comb = getattr(ghg_combustion, attr)
            df_other = df_all.drop(df_comb.index, errors="ignore")
            setattr(extension, attr, df_other)

        return extension

    def _convert_to_co2eq(
        self,
        extension: pymrio.Extension,
    ) -> pymrio.Extension:
        """
        Convert emission values to CO₂-equivalent using multipliers in cst.

        Parameters
        ----------
        extension : pymrio.Extension
            Extension to convert.

        Returns
        -------
        pymrio.Extension
            Converted extension in CO₂-eq.
        """
        extension_output = copy.deepcopy(extension)
        for attr in self.VAR_LIST_NAMES:

            # import and standardize index to gas names only
            df_in = getattr(extension_output, attr)
            df_in.index = pd.Index(
                [name.split(" - ")[0] for name in df_in.index]
            )

            # init df out
            df_out = pd.DataFrame(
                index=pd.Index(cst.MULT_TO_CO2EQ.keys()),
                columns=getattr(extension_output, attr).columns,
            )

            # fill df out
            if attr == cst.UNIT:
                df_out.loc[:, :] = cst.UNIT_GHG_EMISSIONS
            else:
                for gas in df_out.index:
                    if gas in df_in.index:
                        df_out.loc[gas] = df_in.loc[[gas]].sum()
                    else:
                        df_out.loc[gas] = 0.0
                df_out = (1e-9 * df_out
                    .mul(pd.Series(cst.MULT_TO_CO2EQ), axis=0))

            # set df in extension_out
            setattr(extension_output, attr, df_out)
            del df_out

        return extension_output


class EnergyExtractor(ExtensionExtractor):
    """
    Extract energy-related data from EXIOBASE satellite extensions.

    This extractor isolates all rows whose stressor label contains 'Energy',
    and returns them as a standalone `pymrio.Extension`.
    """

    KEY_ENERGY = "Energy"

    def extract(self) -> pymrio.Extension:
        """
        Extract employment (labour) extension.

        Returns
        -------
        pymrio.Extension
            Labour-related extension with employment values.
        """
        is_energy = self._extensions.F.index.str.contains(
            self.KEY_ENERGY, regex=False, case=False
        )

        return self.extract_based_on_bool_index(
            index=is_energy,
            extension_in=self._extensions,
            extension_name=cst.ENERGY,
        )

class RawMaterialsExtractor(ExtensionExtractor):
    """
    Extract and process raw material extraction data from an EXIOBASE MRIO system.

    This class isolates "Domestic Extraction Used" flows from the satellite extension,
    reclassifies them into high-level material categories, and returns a processed
    `pymrio.Extension` object with optional aggregation by category.
    """

    KEY_DOMESTIC_EXTRACTION = "Domestic Extraction Used"

    def extract(self, mapping: bool = False, aggregate: bool = False) -> pymrio.Extension:
        """
        Main method to extract and organize raw material extensions.

        Parameters
        ----------
        aggregate : bool, optional
            Whether to aggregate raw materials by broad category
            (default: True).

        Returns
        -------
        pymrio.Extension
            Extension for raw material extraction, optionally aggregated.
        """
        extension = self._extract_raw_materials()

        # Apply standard reindexing with category/subcategory/sector
        if mapping:
            extension = self.apply_index_mapping(
                extension,
                mapping_dict=cst.RAW_MATERIAL_CATEGORY_MAPPING,
                level_names=[
                    cst.IDX_CATEGORY,
                    cst.IDX_SUB_CATEGORY,
                    cst.IDX_SECTOR,
                ],
            )

        if aggregate:
            extension = self.aggregate_by_top_level(extension)

        return extension

    def _extract_raw_materials(self) -> pymrio.Extension:
        """
        Extract raw material data (Domestic Extraction Used) from the
        EXIOBASE extensions.

        Returns
        -------
        pymrio.Extension
            Raw material flows extension (unaggregated).
        """
        extension_in = self._extensions.copy()
        unit_df = extension_in.unit.reset_index()
        is_raw_material = unit_df.iloc[:, 0].apply(
            lambda x: x.split(" - ")[0] == self.KEY_DOMESTIC_EXTRACTION
        )

        extension_out = self.extract_based_on_bool_index(
            index=is_raw_material,
            extension_in=extension_in,
            extension_name=cst.RAW_MATERIALS,
        )

        # # reindex extension using " - " as a sep
        # reindex dropping key domestic extraction in front of index
        index = getattr(extension_out, cst.UNIT).index
        index = index.str.replace(r"^[^-]+ - ", "", regex=True)
        # index = index.str.split(" - ", expand=True)
        # index = index.droplevel(level=[0, -1])

        for elt in ExtensionExtractor.VAR_LIST_NAMES:
            df = getattr(extension_out, elt)
            df.index = index

        return extension_out


class LabourExtractor(ExtensionExtractor):
    """
    Extract employment-related data from EXIOBASE satellite extensions.

    This extractor isolates all rows whose stressor label starts with 'Employment',
    and returns them as a standalone `pymrio.Extension`.
    """

    KEY_EMPLOYMENT = "Employment"

    def extract(self) -> pymrio.Extension:
        """
        Extract employment (labour) extension.

        Returns
        -------
        pymrio.Extension
            Labour-related extension with employment values.
        """
        is_employment = self._extensions.F.index.str.contains(
            self.KEY_EMPLOYMENT, regex=False, case=False
        )

        return self.extract_based_on_bool_index(
            index=is_employment,
            extension_in=self._extensions,
            extension_name=cst.LABOR,
        )


class ValueAddedExtractor(ExtensionExtractor):
    """
    Extract value added components from EXIOBASE satellite extensions.

    This extractor selects rows corresponding to value added elements
    (e.g. compensation of employees, gross operating surplus, taxes).
    """
    KEYS_VALUE_ADDED = [
        "value added",
        "taxes",
        "compensation",
        "operating surplus"
    ]
    KEY_VALUE_ADDED_UNIT = "M.EUR"

    def extract(self) -> pymrio.Extension:
        """
        Extract value added extension.

        Returns
        -------
        pymrio.Extension
            Extension containing value added components.
        """
        # extension_out = self.extract_by_unit_value(
        #     extension_in=self._extensions,
        #     extension_name=cst.VALUE_ADDED,
        #     target_unit=self.KEY_VALUE_ADDED_UNIT
        # )
        is_value_added = self._extensions.F.index.str.contains(
            "|".join(self.KEYS_VALUE_ADDED),
            case=False,
            regex=True,
        )
        return self.extract_based_on_bool_index(
            index=is_value_added,
            extension_in=self._extensions,
            extension_name=cst.VALUE_ADDED,
        )

class WaterExtractor(ExtensionExtractor):
    """
    Extract water-related environmental flows from EXIOBASE MRIO extensions.

    This extractor filters all rows whose stressor name starts with "Water",
    from the appropriate extension depending on the EXIOBASE version.
    """
    KEY_WATER =  "Water"
    KEY_WATER_UNIT = "Mm3"

    def extract(self, aggregate: bool = False) -> pymrio.Extension:

        extension_out = self._extract_water()

        # # reindex extension using " - " as a sep
        # index = getattr(extension_out, cst.UNIT).index
        # index = index.str.split(" - ", expand=True)
        #
        # for elt in ExtensionExtractor.VAR_LIST_NAMES:
        #     df = getattr(extension_out, elt)
        #     df.index = index
        #
        # if aggregate:
        #     extension = self.aggregate_by_top_level(extension_out, 0)

        return extension_out

    def _extract_water(self) -> pymrio.Extension:
        """
        Extract water stressor extension from EXIOBASE.

        Returns
        -------
        pymrio.Extension
            Water-related environmental extension.
        """
        # extension_out = self.extract_by_unit_value(
        #     extension_in=self._extensions,
        #     extension_name=cst.WATER,
        #     target_unit=self.KEY_WATER_UNIT
        # )
        is_water = self._extensions.F.index.str.contains(
            self.KEY_WATER, regex=False
        )
        return self.extract_based_on_bool_index(
            index=is_water,
            extension_in=self._extensions,
            extension_name=cst.WATER
        )


class LandUseExtractor(ExtensionExtractor):
    """
    Extract land use data from the EXIOBASE MRIO system.

    This extractor filters rows in the environmental extension
    where the unit is equal to "km2", which corresponds to land use flows.
    """
    KEY_LAND_USE_UNIT = "km2"

    def extract(self, aggregate=True) -> pymrio.Extension:
        """
        Extract the land use extension (unit = 'km2').

        Returns
        -------
        pymrio.Extension
            Extension containing land use flows.
        """
        extension_out = self.extract_by_unit_value(
            extension_in=self._extensions,
            extension_name=cst.LAND_USE,
            target_unit=self.KEY_LAND_USE_UNIT,
        )

        # # reindex extension using " - " as a sep
        # index = getattr(extension_out, cst.UNIT).index
        # index = index.str.split(" - ", expand=True)
        #
        # # replace "Perm. meadows &" by "Permanent" in index
        # if self._version in ["3.9.4", "3.9.5"]:
        #     index = pd.MultiIndex.from_arrays(
        #         [
        #             index.get_level_values(0).str.replace(
        #                 "Perm. meadows &", "Permanent"
        #             ),
        #             index.get_level_values(1),
        #             index.get_level_values(2),
        #         ],
        #         names=index.names,
        #     )
        #
        # for elt in ExtensionExtractor.VAR_LIST_NAMES:
        #     df = getattr(extension_out, elt)
        #     df.index = index
        #
        # if aggregate:
        #     extension_out = self.aggregate_by_top_level(extension_out, 0)

        return extension_out

class BiogeochemicalExtractor(ExtensionExtractor):
    """
    Extract biogeochemical-related data from EXIOBASE satellite extensions.

    This extractor isolates all rows whose stressor label starts with on of the
    chemicals specify in KEYS_BIOGEOCHEMICAL
    and returns them as a standalone `pymrio.Extension`.
    """

    KEYS_BIOGEOCHEMICAL = ["N", "NH3", "P"]

    def extract(self) -> pymrio.Extension:
        prefixes = tuple(f"{k} - " for k in self.KEYS_BIOGEOCHEMICAL)

        is_biogeochemical = self._extensions.F.index.str.startswith(prefixes)

        return self.extract_based_on_bool_index(
            index=is_biogeochemical,
            extension_in=self._extensions,
            extension_name=cst.BIOGEOCHEMICAL,
        )
