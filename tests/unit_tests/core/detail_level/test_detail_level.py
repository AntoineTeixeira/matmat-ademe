import pandas as pd


class TestDetailLevel:

    class TestGetFilteredDl:

        def test_no_filters_returns_same_data(self, dl_sectors_2):
            """
            Test function `get_filtered_dl`

            Pass no filters, verify the returned DL has the same dataframe
            as the original and is a new instance of the same class.
            """
            result = dl_sectors_2.get_filtered_dl()

            assert isinstance(result, dl_sectors_2.__class__)
            pd.testing.assert_frame_equal(result.df, dl_sectors_2.df)

        def test_single_filter_applied(self, mocker, dl_sectors_2):
            """
            Test function `get_filtered_dl`

            Pass a single mocked filter, verify apply_to_detail_level is called
            with the original df and the result is built from the filtered df.
            """
            filtered_df = mocker.Mock()
            mock_filter = mocker.Mock()
            mock_filter.apply_to_detail_level.return_value = filtered_df

            result = dl_sectors_2.get_filtered_dl(mock_filter)

            mock_filter.apply_to_detail_level.assert_called_once_with(
                df=dl_sectors_2.df
            )
            assert isinstance(result, dl_sectors_2.__class__)
            assert result.df == filtered_df

        def test_multiple_filters_chained(self, mocker, dl_sectors_2):
            """
            Test function `get_filtered_dl`

            Pass two mocked filters, verify they are applied in order, each
            receiving the output of the previous one.
            """
            df_after_first = mocker.Mock()
            df_after_second = mocker.Mock()

            filter_1 = mocker.Mock()
            filter_1.apply_to_detail_level.return_value = df_after_first
            filter_2 = mocker.Mock()
            filter_2.apply_to_detail_level.return_value = df_after_second

            result = dl_sectors_2.get_filtered_dl(filter_1, filter_2)

            filter_1.apply_to_detail_level.assert_called_once_with(
                df=dl_sectors_2.df
            )
            filter_2.apply_to_detail_level.assert_called_once_with(
                df=df_after_first
            )
            assert result.df == df_after_second
