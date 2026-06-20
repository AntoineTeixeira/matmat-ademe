from matmat.core.dataset.config import DataSetConfig, DataSetMap


class TestDataSetConfig:

    test_map_1 = DataSetMap(
        {
            "config_11": {"A", "B", "C"},
            "config_12": {"X", "Y"},
            "config_13": {"A", "C", "Y"},
            "config_14": {"Z"},
            "config_15": {"Z", "A"},
        }
    )
    test_map_2 = DataSetMap(
        {
            "config_21": {"A", "B", "C"},
            "config_22": {"X", "Y"},
            "config_23": {"A", "Z", "B"},
            "config_24": {"C"},
        }
    )

    def test_get_applicable_set_one_map(self):

        config_ = DataSetConfig(config__1=self.test_map_1)

        for k, v in self.test_map_1.map_.items():
            assert config_.get_applicable_set(config__1=k) == v

    def test_get_applicable_set_several_maps(self):

        config_ = DataSetConfig(
            config__1=self.test_map_1, config__2=self.test_map_2
        )

        for k1, v1 in self.test_map_1.map_.items():
            for k2, v2 in self.test_map_2.map_.items():
                assert (
                    config_.get_applicable_set(
                        config__1=k1,
                        config__2=k2,
                    )
                    == v1 & v2
                )
