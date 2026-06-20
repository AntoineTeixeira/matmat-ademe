import pytest

from matmat.core.accounts.system import builder as s_builder
from matmat.core.accounts.extension import builder as e_builder
from matmat.core.accounts import builder as a_builder
from matmat.core.shocks import builder as as_builder
from matmat.core.shocks.system import builder as ss_builder
from matmat.core.shocks.extension import builder as se_builder

from tests.utils.constants import (
    sectors,
    regions,
    final_demand_categories,
    extension_categories,
)
from tests.utils import builders

# DETAIL LEVELS
# -------------


@pytest.fixture(scope="session")
def dl_sectors_1():
    return sectors.DL_SECTORS_1


@pytest.fixture(scope="session")
def dl_sectors_2():
    return sectors.DL_SECTORS_2


@pytest.fixture(scope="session")
def dl_sectors_3():
    return sectors.DL_SECTORS_3


@pytest.fixture(scope="session")
def dl_regions_1():
    return regions.DL_REGIONS_1


@pytest.fixture(scope="session")
def dl_regions_2():
    return regions.DL_REGIONS_2


@pytest.fixture(scope="session")
def dl_regions_3():
    return regions.DL_REGIONS_3


@pytest.fixture(scope="session")
def dl_final_demand_categories_1():
    return final_demand_categories.DL_FDC_1


@pytest.fixture(scope="session")
def dl_final_demand_categories_2():
    return final_demand_categories.DL_FDC_2


@pytest.fixture(scope="session")
def dl_final_demand_categories_3():
    return final_demand_categories.DL_FDC_3


@pytest.fixture(scope="session")
def dl_extension_categories_1():
    return extension_categories.DL_EXT_CATS_1


@pytest.fixture(scope="session")
def dl_extension_categories_2():
    return extension_categories.DL_EXT_CATS_2


@pytest.fixture(scope="session")
def dl_extension_categories_3():
    return extension_categories.DL_EXT_CATS_3


# BRIDGES
# -------


@pytest.fixture(scope="session")
def bridge_sectors_from_2_to_1():
    return sectors.BRIDGE_SECTORS_FROM_2_TO_1


@pytest.fixture(scope="session")
def bridge_sectors_from_3_to_1():
    return sectors.BRIDGE_SECTORS_FROM_3_TO_1


@pytest.fixture(scope="session")
def bridge_sectors_from_1_to_2():
    return sectors.BRIDGE_SECTORS_FROM_1_TO_2


@pytest.fixture(scope="session")
def bridge_sectors_from_1_to_3():
    return sectors.BRIDGE_SECTORS_FROM_1_TO_3


@pytest.fixture(scope="session")
def multi_bridge_sectors():
    return sectors.MULTI_BRIDGE_SECTORS


@pytest.fixture(scope="session")
def bridge_regions_from_2_to_1():
    return regions.BRIDGE_REGIONS_FROM_2_TO_1


@pytest.fixture(scope="session")
def bridge_regions_from_1_to_2():
    return regions.BRIDGE_REGIONS_FROM_1_TO_2


@pytest.fixture(scope="session")
def bridge_regions_from_1_to_3():
    return regions.BRIDGE_REGIONS_FROM_1_TO_3


@pytest.fixture(scope="session")
def bridge_regions_from_3_to_1():
    return regions.BRIDGE_REGIONS_FROM_3_TO_1


@pytest.fixture(scope="session")
def multi_bridge_regions():
    return regions.MULTI_BRIDGE_REGIONS


@pytest.fixture(scope="session")
def bridge_fdc_from_2_to_1():
    return final_demand_categories.BRIDGE_FDC_FROM_2_TO_1


@pytest.fixture(scope="session")
def bridge_fdc_from_3_to_1():
    return final_demand_categories.BRIDGE_FDC_FROM_3_TO_1


@pytest.fixture(scope="session")
def bridge_fdc_from_1_to_2():
    return final_demand_categories.BRIDGE_FDC_FROM_1_TO_2


@pytest.fixture(scope="session")
def bridge_fdc_from_1_to_3():
    return final_demand_categories.BRIDGE_FDC_FROM_1_TO_3


@pytest.fixture(scope="session")
def multi_bridge_fdc():
    return final_demand_categories.MULTI_BRIDGE_FDC


@pytest.fixture(scope="session")
def bridge_ext_cats_from_2_to_1():
    return extension_categories.BRIDGE_EXT_CATS_FROM_2_TO_1


@pytest.fixture(scope="session")
def bridge_ext_cats_from_3_to_1():
    return extension_categories.BRIDGE_EXT_CATS_FROM_3_TO_1


@pytest.fixture(scope="session")
def bridge_ext_cats_from_1_to_2():
    return extension_categories.BRIDGE_EXT_CATS_FROM_1_TO_2


@pytest.fixture(scope="session")
def bridge_ext_cats_from_1_to_3():
    return extension_categories.BRIDGE_EXT_CATS_FROM_1_TO_3


@pytest.fixture(scope="session")
def multi_bridge_ext_cats():
    return extension_categories.MULTI_BRIDGE_EXT_CATS


# SYSTEMS
# -------


@pytest.fixture(scope="module")
def system_standard_1(
    dl_regions_1, dl_sectors_1, dl_final_demand_categories_1
):
    s_director = s_builder.get_director(reset=True)
    s_director.set_regions(dl_regions_1)
    s_director.set_sectors(dl_sectors_1)
    s_director.set_final_demand_categories(dl_final_demand_categories_1)
    system = s_director.make_standard_system()
    builders.randomize_dataset(system.dataset)
    return system


@pytest.fixture(scope="module")
def system_standard_2(
    dl_regions_2, dl_sectors_2, dl_final_demand_categories_2
):
    s_director = s_builder.get_director(reset=True)
    s_director.set_regions(dl_regions_2)
    s_director.set_sectors(dl_sectors_2)
    s_director.set_final_demand_categories(dl_final_demand_categories_2)
    system = s_director.make_standard_system()
    builders.randomize_dataset(system.dataset)
    return system


@pytest.fixture(scope="module")
def system_standard_3(
    dl_regions_3, dl_sectors_3, dl_final_demand_categories_3
):
    s_director = s_builder.get_director(reset=True)
    s_director.set_regions(dl_regions_3)
    s_director.set_sectors(dl_sectors_3)
    s_director.set_final_demand_categories(dl_final_demand_categories_3)
    system = s_director.make_standard_system()
    builders.randomize_dataset(system.dataset)
    return system


@pytest.fixture(scope="module")
def system_exo_3(dl_regions_3, dl_sectors_3, dl_final_demand_categories_3):
    s_director = s_builder.get_director(reset=True)
    s_director.set_regions(dl_regions_3)
    s_director.set_sectors(dl_sectors_3)
    s_director.set_final_demand_categories(dl_final_demand_categories_3)
    system = s_director.make_exo_invest_matrix_system()
    builders.randomize_dataset(system.dataset)
    return system


@pytest.fixture(scope="module")
def system_endo_3(dl_regions_3, dl_sectors_3, dl_final_demand_categories_3):
    s_director = s_builder.get_director(reset=True)
    s_director.set_regions(dl_regions_3)
    s_director.set_sectors(dl_sectors_3)
    s_director.set_final_demand_categories(dl_final_demand_categories_3)
    system = s_director.make_endo_invest_matrix_system()
    builders.randomize_dataset(system.dataset)
    return system


# EXTENSIONS
# ----------


@pytest.fixture(scope="module")
def extension_use_based_1(
    dl_regions_1,
    dl_sectors_1,
    dl_final_demand_categories_1,
    dl_extension_categories_1,
):
    e_director = e_builder.get_director(reset=True)
    e_director.set_regions(dl_regions_1)
    e_director.set_sectors(dl_sectors_1)
    e_director.set_final_demand_categories(dl_final_demand_categories_1)
    e_director.set_extension_categories(dl_extension_categories_1)
    extension = e_director.make_use_based_extension(
        name=extension_categories.EXT_NAME_USE_BASED
    )
    builders.randomize_dataset(extension.dataset)
    return extension


@pytest.fixture(scope="module")
def extension_gross_output_based_1(
    dl_regions_1,
    dl_sectors_1,
    dl_final_demand_categories_1,
    dl_extension_categories_1,
):
    e_director = e_builder.get_director(reset=True)
    e_director.set_regions(dl_regions_1)
    e_director.set_sectors(dl_sectors_1)
    e_director.set_final_demand_categories(dl_final_demand_categories_1)
    e_director.set_extension_categories(dl_extension_categories_1)
    extension = e_director.make_gross_output_based_extension(
        name=extension_categories.EXT_NAME_GROSS_OUTPUT_BASED
    )
    builders.randomize_dataset(extension.dataset)
    return extension


@pytest.fixture(scope="module")
def extension_embodied_in_import_1(
    dl_regions_1,
    dl_sectors_1,
    dl_final_demand_categories_1,
    dl_extension_categories_1,
):
    e_director = e_builder.get_director(reset=True)
    e_director.set_regions(dl_regions_1)
    e_director.set_sectors(dl_sectors_1)
    e_director.set_final_demand_categories(dl_final_demand_categories_1)
    e_director.set_extension_categories(dl_extension_categories_1)
    extension = e_director.make_embodied_in_import_extension(
        name=extension_categories.EXT_NAME_EMBODIED_IN_IMPORT
    )
    builders.randomize_dataset(extension.dataset)
    return extension


@pytest.fixture(scope="module")
def extension_use_based_2(
    dl_regions_2,
    dl_sectors_2,
    dl_final_demand_categories_2,
    dl_extension_categories_2,
):
    e_director = e_builder.get_director(reset=True)
    e_director.set_regions(dl_regions_2)
    e_director.set_sectors(dl_sectors_2)
    e_director.set_final_demand_categories(dl_final_demand_categories_2)
    e_director.set_extension_categories(dl_extension_categories_2)
    extension = e_director.make_use_based_extension(
        name=extension_categories.EXT_NAME_USE_BASED
    )
    builders.randomize_dataset(extension.dataset)
    return extension


@pytest.fixture(scope="module")
def extension_gross_output_based_2(
    dl_regions_2,
    dl_sectors_2,
    dl_final_demand_categories_2,
    dl_extension_categories_2,
):
    e_director = e_builder.get_director(reset=True)
    e_director.set_regions(dl_regions_2)
    e_director.set_sectors(dl_sectors_2)
    e_director.set_final_demand_categories(dl_final_demand_categories_2)
    e_director.set_extension_categories(dl_extension_categories_2)
    extension = e_director.make_gross_output_based_extension(
        name=extension_categories.EXT_NAME_GROSS_OUTPUT_BASED
    )
    builders.randomize_dataset(extension.dataset)
    return extension


@pytest.fixture(scope="module")
def extension_embodied_in_import_2(
    dl_regions_2,
    dl_sectors_2,
    dl_final_demand_categories_2,
    dl_extension_categories_2,
):
    e_director = e_builder.get_director(reset=True)
    e_director.set_regions(dl_regions_2)
    e_director.set_sectors(dl_sectors_2)
    e_director.set_final_demand_categories(dl_final_demand_categories_2)
    e_director.set_extension_categories(dl_extension_categories_2)
    extension = e_director.make_embodied_in_import_extension(
        name=extension_categories.EXT_NAME_EMBODIED_IN_IMPORT
    )
    builders.randomize_dataset(extension.dataset)
    return extension


@pytest.fixture(scope="module")
def extension_use_based_3(
    dl_regions_3,
    dl_sectors_3,
    dl_final_demand_categories_3,
    dl_extension_categories_3,
):
    e_director = e_builder.get_director(reset=True)
    e_director.set_regions(dl_regions_3)
    e_director.set_sectors(dl_sectors_3)
    e_director.set_final_demand_categories(dl_final_demand_categories_3)
    e_director.set_extension_categories(dl_extension_categories_3)
    extension = e_director.make_use_based_extension(
        name=extension_categories.EXT_NAME_USE_BASED
    )
    builders.randomize_dataset(extension.dataset)
    return extension


@pytest.fixture(scope="module")
def extension_gross_output_based_3(
    dl_regions_3,
    dl_sectors_3,
    dl_final_demand_categories_3,
    dl_extension_categories_3,
):
    e_director = e_builder.get_director(reset=True)
    e_director.set_regions(dl_regions_3)
    e_director.set_sectors(dl_sectors_3)
    e_director.set_final_demand_categories(dl_final_demand_categories_3)
    e_director.set_extension_categories(dl_extension_categories_3)
    extension = e_director.make_gross_output_based_extension(
        name=extension_categories.EXT_NAME_GROSS_OUTPUT_BASED
    )
    builders.randomize_dataset(extension.dataset)
    return extension


@pytest.fixture(scope="module")
def extension_embodied_in_import_3(
    dl_regions_3,
    dl_sectors_3,
    dl_final_demand_categories_3,
    dl_extension_categories_3,
):
    e_director = e_builder.get_director(reset=True)
    e_director.set_regions(dl_regions_3)
    e_director.set_sectors(dl_sectors_3)
    e_director.set_final_demand_categories(dl_final_demand_categories_3)
    e_director.set_extension_categories(dl_extension_categories_3)
    extension = e_director.make_embodied_in_import_extension(
        name=extension_categories.EXT_NAME_EMBODIED_IN_IMPORT
    )
    builders.randomize_dataset(extension.dataset)
    return extension


# ACCOUNTS
# --------


@pytest.fixture(scope="module")
def accounts_1(
    system_standard_1,
    extension_use_based_1,
    extension_gross_output_based_1,
    extension_embodied_in_import_1,
):
    a_director = a_builder.get_director(reset=True)
    return a_director.make_from_system_and_extensions(
        system=system_standard_1,
        extensions={
            extension_use_based_1.name: extension_use_based_1,
            extension_gross_output_based_1.name: extension_gross_output_based_1,
            extension_embodied_in_import_1.name: extension_embodied_in_import_1,
        },
    )


@pytest.fixture(scope="module")
def accounts_2(
    system_standard_2,
    extension_use_based_2,
    extension_gross_output_based_2,
    extension_embodied_in_import_2,
):
    a_director = a_builder.get_director(reset=True)
    return a_director.make_from_system_and_extensions(
        system=system_standard_2,
        extensions={
            extension_use_based_2.name: extension_use_based_2,
            extension_gross_output_based_2.name: extension_gross_output_based_2,
            extension_embodied_in_import_2.name: extension_embodied_in_import_2,
        },
    )


@pytest.fixture(scope="module")
def accounts_3(
    system_standard_3,
    extension_use_based_3,
    extension_gross_output_based_3,
    extension_embodied_in_import_3,
):
    a_director = a_builder.get_director(reset=True)
    return a_director.make_from_system_and_extensions(
        system=system_standard_3,
        extensions={
            extension_use_based_3.name: extension_use_based_3,
            extension_gross_output_based_3.name: extension_gross_output_based_3,
            extension_embodied_in_import_3.name: extension_embodied_in_import_3,
        },
    )


# SYSTEM SHOCKS
# -------------
@pytest.fixture(scope="module")
def system_shock_standard_1(
    dl_regions_1,
    dl_sectors_1,
    dl_final_demand_categories_1,
):
    ss_director = ss_builder.get_director(reset=True)
    ss_director.set_regions(dl_regions_1)
    ss_director.set_sectors(dl_sectors_1)
    ss_director.set_final_demand_categories(dl_final_demand_categories_1)
    system_shock = ss_director.make_shock_standard()
    builders.randomize_dataset(system_shock.dataset)
    return system_shock


@pytest.fixture(scope="module")
def system_shock_standard_2(
    dl_regions_2,
    dl_sectors_2,
    dl_final_demand_categories_2,
):
    ss_director = ss_builder.get_director(reset=True)
    ss_director.set_regions(dl_regions_2)
    ss_director.set_sectors(dl_sectors_2)
    ss_director.set_final_demand_categories(dl_final_demand_categories_2)
    system_shock = ss_director.make_shock_standard()
    builders.randomize_dataset(system_shock.dataset)
    return system_shock


@pytest.fixture(scope="module")
def system_shock_standard_3(
    dl_regions_3,
    dl_sectors_3,
    dl_final_demand_categories_3,
):
    ss_director = ss_builder.get_director(reset=True)
    ss_director.set_regions(dl_regions_3)
    ss_director.set_sectors(dl_sectors_3)
    ss_director.set_final_demand_categories(dl_final_demand_categories_3)
    system_shock = ss_director.make_shock_standard()
    builders.randomize_dataset(system_shock.dataset)
    return system_shock


# EXTENSIONS SHOCKS
# -----------------
@pytest.fixture(scope="module")
def extension_shock_use_based_1(
    dl_regions_1,
    dl_sectors_1,
    dl_final_demand_categories_1,
    dl_extension_categories_1,
):
    se_director = se_builder.get_director(reset=True)
    se_director.set_regions(dl_regions_1)
    se_director.set_sectors(dl_sectors_1)
    se_director.set_final_demand_categories(dl_final_demand_categories_1)
    se_director.set_extension_categories(dl_extension_categories_1)
    extension_shock = se_director.make_shock_s_y(
        name=extension_categories.EXT_NAME_USE_BASED
    )
    builders.randomize_dataset(extension_shock.dataset)
    return extension_shock


@pytest.fixture(scope="module")
def extension_shock_gross_output_based_1(
    dl_regions_1,
    dl_sectors_1,
    dl_final_demand_categories_1,
    dl_extension_categories_1,
):
    se_director = se_builder.get_director(reset=True)
    se_director.set_regions(dl_regions_1)
    se_director.set_sectors(dl_sectors_1)
    se_director.set_final_demand_categories(dl_final_demand_categories_1)
    se_director.set_extension_categories(dl_extension_categories_1)
    extension_shock = se_director.make_shock_s_x(
        name=extension_categories.EXT_NAME_GROSS_OUTPUT_BASED
    )
    builders.randomize_dataset(extension_shock.dataset)
    return extension_shock


@pytest.fixture(scope="module")
def extension_shock_embodied_in_import_1(
    dl_regions_1,
    dl_sectors_1,
    dl_final_demand_categories_1,
    dl_extension_categories_1,
):
    se_director = se_builder.get_director(reset=True)
    se_director.set_regions(dl_regions_1)
    se_director.set_sectors(dl_sectors_1)
    se_director.set_final_demand_categories(dl_final_demand_categories_1)
    se_director.set_extension_categories(dl_extension_categories_1)
    extension_shock = se_director.make_shock_m_row(
        name=extension_categories.EXT_NAME_EMBODIED_IN_IMPORT
    )
    builders.randomize_dataset(extension_shock.dataset)
    return extension_shock


@pytest.fixture(scope="module")
def extension_shock_use_based_2(
    dl_regions_2,
    dl_sectors_2,
    dl_final_demand_categories_2,
    dl_extension_categories_2,
):
    se_director = se_builder.get_director(reset=True)
    se_director.set_regions(dl_regions_2)
    se_director.set_sectors(dl_sectors_2)
    se_director.set_final_demand_categories(dl_final_demand_categories_2)
    se_director.set_extension_categories(dl_extension_categories_2)
    extension_shock = se_director.make_shock_s_y(
        name=extension_categories.EXT_NAME_USE_BASED
    )
    builders.randomize_dataset(extension_shock.dataset)
    return extension_shock


@pytest.fixture(scope="module")
def extension_shock_gross_output_based_2(
    dl_regions_2,
    dl_sectors_2,
    dl_final_demand_categories_2,
    dl_extension_categories_2,
):
    se_director = se_builder.get_director(reset=True)
    se_director.set_regions(dl_regions_2)
    se_director.set_sectors(dl_sectors_2)
    se_director.set_final_demand_categories(dl_final_demand_categories_2)
    se_director.set_extension_categories(dl_extension_categories_2)
    extension_shock = se_director.make_shock_s_x(
        name=extension_categories.EXT_NAME_GROSS_OUTPUT_BASED
    )
    builders.randomize_dataset(extension_shock.dataset)
    return extension_shock


@pytest.fixture(scope="module")
def extension_shock_embodied_in_import_2(
    dl_regions_2,
    dl_sectors_2,
    dl_final_demand_categories_2,
    dl_extension_categories_2,
):
    se_director = se_builder.get_director(reset=True)
    se_director.set_regions(dl_regions_2)
    se_director.set_sectors(dl_sectors_2)
    se_director.set_final_demand_categories(dl_final_demand_categories_2)
    se_director.set_extension_categories(dl_extension_categories_2)
    extension_shock = se_director.make_shock_m_row(
        name=extension_categories.EXT_NAME_EMBODIED_IN_IMPORT
    )
    builders.randomize_dataset(extension_shock.dataset)
    return extension_shock


@pytest.fixture(scope="module")
def extension_shock_use_based_3(
    dl_regions_3,
    dl_sectors_3,
    dl_final_demand_categories_3,
    dl_extension_categories_3,
):
    se_director = se_builder.get_director(reset=True)
    se_director.set_regions(dl_regions_3)
    se_director.set_sectors(dl_sectors_3)
    se_director.set_final_demand_categories(dl_final_demand_categories_3)
    se_director.set_extension_categories(dl_extension_categories_3)
    extension_shock = se_director.make_shock_s_y(
        name=extension_categories.EXT_NAME_USE_BASED
    )
    builders.randomize_dataset(extension_shock.dataset)
    return extension_shock


@pytest.fixture(scope="module")
def extension_shock_gross_output_based_3(
    dl_regions_3,
    dl_sectors_3,
    dl_final_demand_categories_3,
    dl_extension_categories_3,
):
    se_director = se_builder.get_director(reset=True)
    se_director.set_regions(dl_regions_3)
    se_director.set_sectors(dl_sectors_3)
    se_director.set_final_demand_categories(dl_final_demand_categories_3)
    se_director.set_extension_categories(dl_extension_categories_3)
    extension_shock = se_director.make_shock_s_x(
        name=extension_categories.EXT_NAME_GROSS_OUTPUT_BASED
    )
    builders.randomize_dataset(extension_shock.dataset)
    return extension_shock


@pytest.fixture(scope="module")
def extension_shock_embodied_in_import_3(
    dl_regions_3,
    dl_sectors_3,
    dl_final_demand_categories_3,
    dl_extension_categories_3,
):
    se_director = se_builder.get_director(reset=True)
    se_director.set_regions(dl_regions_3)
    se_director.set_sectors(dl_sectors_3)
    se_director.set_final_demand_categories(dl_final_demand_categories_3)
    se_director.set_extension_categories(dl_extension_categories_3)
    extension_shock = se_director.make_shock_m_row(
        name=extension_categories.EXT_NAME_EMBODIED_IN_IMPORT
    )
    builders.randomize_dataset(extension_shock.dataset)
    return extension_shock


# ACCOUNTS SHOCKS
# ---------------
@pytest.fixture(scope="module")
def accounts_shock_1(
    system_shock_standard_1,
    extension_shock_use_based_1,
    extension_shock_gross_output_based_1,
    extension_shock_embodied_in_import_1,
):
    as_director = as_builder.get_director(reset=True)
    return as_director.make_from_system_and_extensions_shocks(
        system_shock=system_shock_standard_1,
        extensions_shocks={
            extension_shock_use_based_1.name: extension_shock_use_based_1,
            extension_shock_gross_output_based_1.name: extension_shock_gross_output_based_1,
            extension_shock_embodied_in_import_1.name: extension_shock_embodied_in_import_1,
        },
    )


@pytest.fixture(scope="module")
def accounts_shock_2(
    system_shock_standard_2,
    extension_shock_use_based_2,
    extension_shock_gross_output_based_2,
    extension_shock_embodied_in_import_2,
):
    as_director = as_builder.get_director(reset=True)
    return as_director.make_from_system_and_extensions_shocks(
        system_shock=system_shock_standard_2,
        extensions_shocks={
            extension_shock_use_based_2.name: extension_shock_use_based_2,
            extension_shock_gross_output_based_2.name: extension_shock_gross_output_based_2,
            extension_shock_embodied_in_import_2.name: extension_shock_embodied_in_import_2,
        },
    )


@pytest.fixture(scope="module")
def accounts_shock_3(
    system_shock_standard_3,
    extension_shock_use_based_3,
    extension_shock_gross_output_based_3,
    extension_shock_embodied_in_import_3,
):
    as_director = as_builder.get_director(reset=True)
    return as_director.make_from_system_and_extensions_shocks(
        system_shock=system_shock_standard_3,
        extensions_shocks={
            extension_shock_use_based_3.name: extension_shock_use_based_3,
            extension_shock_gross_output_based_3.name: extension_shock_gross_output_based_3,
            extension_shock_embodied_in_import_3.name: extension_shock_embodied_in_import_3,
        },
    )
