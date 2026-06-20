"""
Presentation
************
This module contains classes gathering methods to deal with various file
formats

Content
*******
- Classes:
    - :class:`AbstractFormat`
    - :class:`PickleFormat`
    - :class:`CsvFormat`
    - :class:`ExcelFormat`
    - :class:`NullFormat`
"""

__all__ = [
    "AbstractFormat",
    "PickleFormat",
    "CsvFormat",
    "ExcelFormat",
    "NullFormat",
]

import os
from abc import ABC, abstractmethod

import pandas as pd
import math

from matmat.utils.errors import (
    file_not_found_error_handler,
    MEExcelFileNotReadable,
)
import matmat.utils.logging as log
import matmat.utils.constants as cst


class AbstractFormat(ABC):
    """
    Abstract class representing a file format. It defines a set of abstract
    methods to be implemented by concrete format subclasses.
    """

    NAME: str
    EXTENSION: str

    @abstractmethod
    def read(
        self,
        *,
        path: str,
        file_name: str,
        data_name: str,
        sheet_name: str | int = 0,
        nb_levels_rows: int = None,
        nb_levels_columns: int = None,
    ) -> pd.DataFrame:
        """
        Reads a file and returns the corresponding dataframe.

        The rows and columns levels number are used to read easily the rows
        and columns index. If set to None, then the reader tries to find them.

        Parameters:
            path (str):
                The path to the directory containing the file
            file_name (str):
                The name of the file (without extension)
            data_name (str):
                The name of the data represented in the file
            sheet_name (str | int):
                The name of the sheet containing the data, if applicable (default to 0)
            nb_levels_rows (int):
                The number of levels in the rows index (default to None)
            nb_levels_columns (int):
                The number of levels in the columns index (default to None)
        Returns:
            pd.DataFrame : the read dataframe
        """

    @abstractmethod
    def export(self, df: pd.DataFrame, path: str, file_name: str):
        pass

    @staticmethod
    def is_null() -> bool:
        return False

    @property
    def name(self):
        return self.NAME

    @property
    def extension(self):
        return self.EXTENSION


class PickleFormat(AbstractFormat):
    """
    Class representing the Pickle format
    """

    NAME = cst.FORMAT_PICKLE
    EXTENSION = "pkl"

    @file_not_found_error_handler
    def read(
        self,
        *,
        path: str,
        file_name: str,
        data_name: str,
        sheet_name: str | int = 0,
        nb_levels_rows: int = None,
        nb_levels_columns: int = None,
    ) -> pd.DataFrame:
        full_path = f"{os.path.join(path, file_name)}.{self.EXTENSION}"
        log.verbose(f"Load data {data_name} from {full_path}")
        return pd.read_pickle(full_path)

    def export(self, df: pd.DataFrame, path: str, file_name: str):
        df.to_pickle(f"{os.path.join(path, file_name)}.{self.EXTENSION}")


class CsvFormat(AbstractFormat):
    """
    Class representing the Csv format
    """

    NAME = cst.FORMAT_CSV
    EXTENSION = "csv"

    @staticmethod
    def execute_post_treatment_on_rows_and_columns_index(df: pd.DataFrame):
        # This post-treatment is executed only if:
        #     - The columns is a regular Index
        #     - With a name set to None
        #     - The first line contains only NaN
        if (
            not isinstance(df.columns, pd.MultiIndex)
            and isinstance(df.columns, pd.Index)
            and df.columns.name is None
            and df.iloc[0].isna().all()
        ):
            # Build the columns MultiIndex with the first value in index.names
            df.columns = pd.MultiIndex.from_arrays(
                [df.columns], names=[df.index.names[0]]
            )
            # Update the rows MultiIndex names from the first row index values
            df.index.set_names(df.index[0], inplace=True)
            # Drop the first line
            df.drop(df.index[0], inplace=True)

        # This post-treatment is performed if dealing with regular Index
        # Transform simple Index to MultiIndex if applicable
        if (
            not isinstance(df.index, pd.MultiIndex)
            and len(df.index.names) == 1
        ):
            df.index = pd.MultiIndex.from_arrays(
                [df.index], names=[df.index.names[0]]
            )
        if (
            not isinstance(df.columns, pd.MultiIndex)
            and len(df.columns.names) == 1
        ):
            df.columns = pd.MultiIndex.from_arrays(
                [df.columns], names=[df.columns.names[0]]
            )

    @file_not_found_error_handler
    def read(
        self,
        *,
        path: str,
        file_name: str,
        data_name: str,
        sheet_name: str | int = 0,
        nb_levels_rows: int = None,
        nb_levels_columns: int = None,
    ) -> pd.DataFrame:

        full_path = f"{os.path.join(path, file_name)}.{self.EXTENSION}"
        log.verbose(f"Load data {data_name} from {full_path}")

        if nb_levels_rows is None or nb_levels_columns is None:
            df_read = self._find_df(path=full_path)

        else:
            df_read = pd.read_csv(
                full_path,
                header=list(range(nb_levels_columns)),
                index_col=list(range(nb_levels_rows)),
            )

        self.execute_post_treatment_on_rows_and_columns_index(df=df_read)
        return df_read

    def export(self, df: pd.DataFrame, path: str, file_name: str):
        df.to_csv(f"{os.path.join(path, file_name)}.{self.EXTENSION}")

    @file_not_found_error_handler
    def _find_df(self, path: str) -> pd.DataFrame:
        header, index_col = self._find_header_and_index_col(
            pd.read_csv(path, header=None)
        )
        structured_df = pd.read_csv(path, header=header, index_col=index_col)
        return structured_df

    @staticmethod
    def _find_header_and_index_col(df_raw: pd.DataFrame) -> tuple[list, list]:
        """
        Find the header and index_col parameters used to read a dataframe in a
        CSV file

        Constraint: the first value of the dataframe must be numeric
        (NaN won't work), except for 'unit' data where a specific check on
        the column named 'unit' is done.

        Parameters:
            df_raw (pd.DataFrame):
                The raw dataframe (i.e. without setting header and index_col)
        """
        # Specific case of unit dataframe (which is a string dataframe)
        # The first line contains "unit"
        # Just search at which column this cell is
        for col_idx in range(len(df_raw.columns)):
            # Avoid useless computation
            if col_idx > cst.MAX_NUMBER_OF_MULTI_INDEX_LEVELS:
                break
            cell = df_raw.iloc[0, col_idx]
            if cell == cst.UNIT:
                return list(range(1)), list(range(col_idx))

        first_value_row = None
        first_value_column = None
        # Go through raw dataframe to find header and index_col parameters
        for i in range(len(df_raw.index)):
            for j in range(len(df_raw.columns)):
                data_to_check = df_raw.iloc[i, j]
                # First value is an integer or a float, and is not a NaN
                try:
                    value = float(data_to_check)
                    if not math.isnan(value):
                        try:
                            prev_data_to_check = df_raw.iloc[i - 1, j]
                            try:
                                if math.isnan(float(prev_data_to_check)):
                                    first_value_row = i - 1
                                else:
                                    first_value_row = i
                            # ValueError is raised if the conversion to float
                            # is not possible
                            except ValueError:
                                first_value_row = i
                        # IndexError is raised if index 'i - 1' is out of
                        # bounds
                        except IndexError:
                            first_value_row = i
                        first_value_column = j
                        break
                # ValueError is raised if the conversion to float
                # is not possible
                except ValueError:
                    continue
            if first_value_row is not None and first_value_column is not None:
                break
        if first_value_row is None:
            first_value_row = 1
        if first_value_column is None:
            first_value_column = 1
        return list(range(first_value_row)), list(range(first_value_column))


class ExcelFormat(AbstractFormat):
    """
    Class representing the Excel format
    """

    NAME = cst.FORMAT_EXCEL
    EXTENSION = "xlsx"

    @staticmethod
    def execute_post_treatment_on_rows_and_columns_index(df: pd.DataFrame):
        # This post-treatment is executed only if:
        #     - The columns is a regular Index
        #     - With a name set to None
        #     - The first line contains only NaN
        if (
            not isinstance(df.columns, pd.MultiIndex)
            and isinstance(df.columns, pd.Index)
            and df.columns.name is None
            and df.iloc[0].isna().all()
        ):
            # Build the columns MultiIndex with the last value in index.names
            df.columns = pd.MultiIndex.from_arrays(
                [df.columns], names=[df.index.names[-1]]
            )
            # Update the rows MultiIndex names from the first row index values
            df.index.set_names(df.index[0], inplace=True)
            # Drop the first line
            df.drop(df.index[0], inplace=True)

        # This post-treatment is performed if dealing with regular Index
        # Transform simple Index to MultiIndex if applicable
        if (
            not isinstance(df.index, pd.MultiIndex)
            and len(df.index.names) == 1
        ):
            df.index = pd.MultiIndex.from_arrays(
                [df.index], names=[df.index.names[0]]
            )
        if (
            not isinstance(df.columns, pd.MultiIndex)
            and len(df.columns.names) == 1
        ):
            df.columns = pd.MultiIndex.from_arrays(
                [df.columns], names=[df.columns.names[0]]
            )

    @file_not_found_error_handler
    def read(
        self,
        *,
        path: str,
        file_name: str,
        data_name: str,
        sheet_name: str | int = 0,
        nb_levels_rows: int = None,
        nb_levels_columns: int = None,
    ) -> pd.DataFrame:

        full_path = f"{os.path.join(path, file_name)}.{self.EXTENSION}"
        msg = f"Load data {data_name} from {full_path}"
        if isinstance(sheet_name, str):
            msg += f" at sheet '{sheet_name}'"
        log.verbose(msg)

        if nb_levels_rows is None or nb_levels_columns is None:
            df_read = self._find_df(path=full_path, sheet_name=sheet_name)

        else:
            df_read = pd.read_excel(
                full_path,
                sheet_name=sheet_name,
                header=list(range(nb_levels_columns)),
                index_col=list(range(nb_levels_rows)),
            )

        self.execute_post_treatment_on_rows_and_columns_index(df=df_read)
        return df_read

    def export(self, df: pd.DataFrame, path: str, file_name: str):
        df.to_excel(f"{os.path.join(path, file_name)}.{self.EXTENSION}")

    @file_not_found_error_handler
    def _find_df(
        self,
        path: str,
        sheet_name: str | int = 0,
    ) -> pd.DataFrame:
        header, index_col = self._find_header_and_index_col(
            df_raw=pd.read_excel(path, sheet_name=sheet_name, header=None),
            file_name=os.path.basename(path),
        )
        structured_df = pd.read_excel(
            path, sheet_name=sheet_name, header=header, index_col=index_col
        )
        return structured_df

    def _find_header_and_index_col(
        self,
        df_raw: pd.DataFrame,
        file_name: str,
    ) -> tuple[list, list]:
        """
        Find the header and index_col parameters used to read a dataframe in an
        Excel file.

        Case 1:
            If the dataframe is a unit dataframe, then we use the cst.UNIT marker to
            find the header and index_col parameters.

        Case 2:
            If the dataframe starts with an empty cell, then we look for the closest
            cells (going right and down) containing text, which gives us the header
            and the index_col parameters.

        Case 3:
            If the dataframe does not start with an empty cell, then we look for the
            first numeric cell which is not NaN, which gives us the header and the
            index_col parameters.

        Parameters:
            df_raw (pd.DataFrame):
                The raw dataframe (i.e. without setting header and index_col)
            file_name (str):
                The name of the file being read (for log purpose)

        Returns:
            tuple[list, list] : the header and index_col to use in function pd.read_excel
        """

        # Specific case of unit dataframe (which is a string dataframe)
        # #############################################################
        # The first line contains "unit"
        # Just search at which column this cell is
        for col_idx in range(len(df_raw.columns)):
            # Avoid useless computation
            if col_idx > cst.MAX_NUMBER_OF_MULTI_INDEX_LEVELS:
                break
            cell = df_raw.iloc[0, col_idx]
            if cell == cst.UNIT:
                return list(range(1)), list(range(col_idx))

        # General case of a float dataframe
        # #################################
        # Case when the first cell is empty
        # In this case, we are dealing with MultiIndex in both rows and columns
        first_cell = df_raw.iloc[0, 0]
        if isinstance(first_cell, float) and math.isnan(first_cell):
            header, index_col = (
                self._find_header_and_index_col_in_case_of_multi_index(
                    df_raw=df_raw, file_name=file_name
                )
            )

        # Case when the first cell is not empty
        # In this case, we are dealing with a simple rows or simple columns Index
        else:
            header, index_col = (
                self._find_header_and_index_col_in_case_of_single_index(
                    df_raw=df_raw, file_name=file_name
                )
            )

        header = header if header != 0 else 1
        index_col = index_col if index_col != 0 else 1
        return list(range(header)), list(range(index_col))

    @staticmethod
    def _find_header_and_index_col_in_case_of_multi_index(
        df_raw: pd.DataFrame,
        file_name: str,
    ) -> tuple[int, int]:
        """
        Look for the closest cells (going right and down) containing text,
        which gives us the header and the index_col parameters.

        Parameters:
            df_raw (pd.DataFrame):
                The raw dataframe (i.e. without setting header and index_col)
            file_name (str):
                The name of the file being read (for log purpose)

        Returns:
            tuple[list, list] : the header and index_col to use in function pd.read_excel
        """
        header: int = 0
        index_col: int = 0

        # Loop on rows until we find text
        for row_idx in range(len(df_raw.index)):
            if not isinstance(df_raw.iloc[row_idx, 0], str):
                continue
            else:
                header = row_idx
                break

        # Loop on columns until we find an empty cell
        for col_idx in range(len(df_raw.columns)):
            cell_value = df_raw.iloc[header, col_idx]
            if isinstance(cell_value, float) and math.isnan(cell_value):
                index_col = col_idx
                break

        return header, index_col

    @staticmethod
    def _find_header_and_index_col_in_case_of_single_index(
        df_raw: pd.DataFrame,
        file_name: str,
    ) -> tuple[int, int]:
        """
        Look for the first numeric cell which is not NaN, which gives us the header and the
        index_col parameters. Deal with the case when there is an empty line between the
        numeric cells and the columns index by decrementing the header by 1.

        Parameters:
            df_raw (pd.DataFrame):
                The raw dataframe (i.e. without setting header and index_col)
            file_name (str):
                The name of the file being read (for log purpose)

        Returns:
            tuple[list, list] : the header and index_col to use in function pd.read_excel

        Raises:
            MEExcelFileNotReadable : It is required to have a not-null number at the top-left
                                     of the table (where the data start), otherwise the method
                                     can't compute the header and index_col parameters.
        """
        header: int = -1
        index_col: int = -1

        for col_idx in range(len(df_raw.columns)):

            # Avoid useless computation
            if col_idx > cst.MAX_NUMBER_OF_MULTI_INDEX_LEVELS:
                break

            for row_idx in range(len(df_raw.index)):

                # Avoid useless computation
                if row_idx > cst.MAX_NUMBER_OF_MULTI_INDEX_LEVELS:
                    break

                cell_value = df_raw.iloc[row_idx, col_idx]
                if (
                    isinstance(cell_value, float)
                    or isinstance(cell_value, int)
                ) and not math.isnan(cell_value):

                    header = row_idx
                    index_col = col_idx

                    # Check if the cell above is empty
                    # If True, this means there is an empty line which will be
                    # ignored by Pandas Excel reader
                    # The header shall be decremented
                    try:
                        prev_cell_value = df_raw.iloc[row_idx - 1, col_idx]
                        if isinstance(prev_cell_value, float) and math.isnan(
                            prev_cell_value
                        ):
                            header = row_idx - 1
                        else:
                            header = row_idx
                    except IndexError:
                        pass

                    break

            if header != -1 and index_col != -1:
                break

        if header == -1 and index_col == -1:
            raise MEExcelFileNotReadable(
                file=file_name,
                msg="There shall be a non-null number at the top-left "
                "of the Excel table. It is necessary for the reader to "
                "locate the rows and columns index.",
            )

        return header, index_col


class NullFormat(AbstractFormat):
    """
    Class representing the null format (the methods do nothing)
    """

    NAME = ""
    EXTENSION = "null"

    @staticmethod
    def is_null() -> bool:
        return True

    def read(
        self,
        *,
        path: str,
        file_name: str,
        data_name: str,
        sheet_name: str | int = 0,
        nb_levels_rows: int = None,
        nb_levels_columns: int = None,
    ) -> pd.DataFrame:
        pass

    def export(self, df: pd.DataFrame, path: str, file_name: str):
        pass
