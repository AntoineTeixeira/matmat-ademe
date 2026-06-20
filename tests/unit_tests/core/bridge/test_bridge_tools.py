from matmat.core.bridge.tools import filter_ec_bridges


class TestBridgeTools:

    def test_filter_ec_bridges_no_ext_cats(
        self,
        bridge_sectors_from_3_to_1,
        bridge_regions_from_3_to_1,
        bridge_fdc_from_3_to_1,
    ):
        """
        Test function `filter_ec_bridges`

        All bridges are returned when none are extension categories bridges.
        """
        bridges = (
            bridge_sectors_from_3_to_1,
            bridge_regions_from_3_to_1,
            bridge_fdc_from_3_to_1,
        )
        result = filter_ec_bridges(bridges, "any_extension")
        assert result == list(bridges)

    def test_filter_ec_bridges_ext_cats_matching(
        self, bridge_ext_cats_from_3_to_1
    ):
        """
        Test function `filter_ec_bridges`

        Only the ext_cats bridge with the matching extension_name is returned.
        """
        bridge_other = bridge_ext_cats_from_3_to_1.copy()
        bridge_other.sheet_name = "other_extension"

        bridges = (bridge_ext_cats_from_3_to_1, bridge_other)
        result = filter_ec_bridges(
            bridges, bridge_ext_cats_from_3_to_1.extension_name
        )
        assert result == [bridge_ext_cats_from_3_to_1]

    def test_filter_ec_bridges_ext_cats_no_match(
        self, bridge_ext_cats_from_3_to_1
    ):
        """
        Test function `filter_ec_bridges`

        Empty list is returned when the ext_cats bridge extension_name does not match.
        """
        bridges = (bridge_ext_cats_from_3_to_1,)
        result = filter_ec_bridges(bridges, "non_matching_extension")
        assert result == []

    def test_filter_ec_bridges_mixed(
        self,
        bridge_sectors_from_3_to_1,
        bridge_regions_from_3_to_1,
        bridge_ext_cats_from_3_to_1,
    ):
        """
        Test function `filter_ec_bridges`

        Mixed tuple: non-ext_cats bridges are always returned, ext_cats bridge only
        when extension_name matches.
        """
        bridges = (
            bridge_sectors_from_3_to_1,
            bridge_regions_from_3_to_1,
            bridge_ext_cats_from_3_to_1,
        )
        matching_name = bridge_ext_cats_from_3_to_1.extension_name

        result_match = filter_ec_bridges(bridges, matching_name)
        assert result_match == list(bridges)

        result_no_match = filter_ec_bridges(bridges, "non_matching_extension")
        assert result_no_match == [
            bridge_sectors_from_3_to_1,
            bridge_regions_from_3_to_1,
        ]

    def test_filter_ec_bridges_empty(self):
        """
        Test function `filter_ec_bridges`

        Empty tuple returns empty list.
        """
        result = filter_ec_bridges((), "any_extension")
        assert result == []
