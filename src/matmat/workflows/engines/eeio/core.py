"""
Presentation
************
This module is the 'eeio' module of the
package `engines`.
It defines the eeio engine.

This engine takes as input:
    - an accounts
    - an accounts shock (optional)
    - bridges (optional)
and performs the following treatments:
    - If a shock and bridges are given, disaggregate the shock
      (with the bridge) to match the accounts detail levels
    - Apply calculation strategies
    - If a shock is given, apply the shock to the accounts
    - Calculate the accounts
    - Save the accounts

Content
*******
- Classes:
    - :class:`EngineEEIO`
"""

import os

from matmat.workflows.engines.core import AbstractEngine
from matmat.workflows.engines.eeio.identity import EngineEEIOIdentity
from matmat.core.accounts import builder as a_builder
from matmat.core.shocks import builder as as_builder
from matmat.core.bridge import factory as bridge_factory
from matmat.utils import logging as log


class EngineEEIO(AbstractEngine):

    # Identity
    _id: EngineEEIOIdentity

    KEY_ACCOUNTS = "accounts"
    KEY_SHOCK = "shock"

    @classmethod
    def name(cls):
        return "eeio"

    def load(self):
        self._load_accounts()
        self._load_shock()
        if self._is_shock_loaded():
            self._load_bridges()

    def _load_accounts(self):
        """
        Load accounts

        Fill self.input_data[self.KEY_ACCOUNTS]
        """
        log.info("### LOAD ACCOUNTS ###")
        self.input_data[self.KEY_ACCOUNTS] = a_builder.get_director(
            reset=True
        ).make_from_path(
            path=self.path_in.accounts,
            extensions_names=self._id.extension_names,
            load_data=True,
        )

    def _load_shock(self):
        """
        Load accounts shock if applicable

        Fill self.input_data[self.KEY_SHOCK]
        """
        try:
            path_to_shock = self.path_in.shock
        except AttributeError:
            path_to_shock = None

        if not (path_to_shock is None or path_to_shock == ""):
            log.info("### LOAD SHOCK ###")
            self.input_data[self.KEY_SHOCK] = as_builder.get_director(
                reset=True
            ).make_from_path(
                path=self.path_in.shock,
                extensions_names=self._id.extension_names,
                raise_error_if_extension_not_found=False,
                load_data=True,
            )
        else:
            log.info("No shock given. Go to next step.")

    def _is_shock_loaded(self) -> bool:
        """
        Returns True if shock data are available in
        self.input_data[self.KEY_SHOCK], False otherwise
        """
        return self.KEY_SHOCK in self.input_data.keys()

    def _load_bridges(self):
        """
        Load bridges if applicable

        Fill self.input_data[self.KEY_BRIDGES]
        """
        try:
            path_to_bridges = self.path_in.bridges
        except AttributeError:
            path_to_bridges = None

        if not (path_to_bridges is None or path_to_bridges == ""):
            log.info("### LOAD BRIDGES ###")
            self.input_data[self.KEY_BRIDGES] = (
                bridge_factory.make_bridge_dict_from_path(
                    path=os.path.dirname(path_to_bridges),
                    file_name=os.path.basename(path_to_bridges),
                    extension_names=self.id.extension_names,
                )
            )
        else:
            log.info("No bridge(s) given. Go to next step.")

    def _are_bridges_loaded(self) -> bool:
        """
        Returns True if bridges data are available in
        self.input_data[self.KEY_BRIDGES], False otherwise
        """
        return self.KEY_BRIDGES in self.input_data.keys()

    def process(self):
        if self._is_shock_loaded():
            self._disaggregate_shock()
        self._apply_calcul_strategies()

    def _disaggregate_shock(self):
        """
        Disaggregate shock with bridge if applicable (i.e. if bridges
        are given)

        Fill self.processed_data[self.KEY_SHOCK]
        """
        shock = self.input_data[self.KEY_SHOCK].copy()
        if self._are_bridges_loaded():
            log.info("### DISAGGREGATE SHOCK ###")
            # Apply bridges one by one to make debugging easier if necessary
            for bridge_ in self.get_input_data(self.KEY_BRIDGES).values():
                if isinstance(bridge_, dict):
                    for bridge_ext_cats in bridge_.values():
                        shock.disaggregate(bridge_ext_cats)
                else:
                    shock.disaggregate(bridge_)
        self.processed_data[self.KEY_SHOCK] = shock

    def _is_shock_processed(self):
        """
        Returns True if shock data are available in
        self.processed_data[self.KEY_SHOCK], False otherwise
        """
        return self.KEY_SHOCK in self.processed_data.keys()

    def _apply_calcul_strategies(self):
        """
        Apply calculation strategies

        Fill self.processed_data[self.KEY_ACCOUNTS]
        """
        log.info("### APPLY CALCUL STRATEGIES ###")
        accounts = self.input_data[self.KEY_ACCOUNTS].copy()
        accounts.system.calcul = self._id.system_calcul_strategy
        self.processed_data[self.KEY_ACCOUNTS] = accounts

    def calculate(self):
        self._shock_accounts()
        self._calculate_accounts()
        if self._id.shall_calculate_mapping:
            self._calculate_mapping()

    def _shock_accounts(self):
        """
        Apply shock to accounts:
            - Reset accounts for shock
            - Shock accounts
            - Calculate accounts

        Fill self.calculated_data[self.KEY_ACCOUNTS]
        """
        accounts = self.processed_data[self.KEY_ACCOUNTS].copy()
        if self._is_shock_processed():
            log.info("### SHOCK ACCOUNTS ###")
            accounts.reset_for_shock()
            accounts.shock(
                shock=self.processed_data[self.KEY_SHOCK],
            )
        self.calculated_data[self.KEY_ACCOUNTS] = accounts

    def _calculate_accounts(self):
        """
        Calculate accounts

        Update self.calculated_data[self.KEY_ACCOUNTS]
        """
        log.info("### CALCULATE ACCOUNTS ###")
        accounts = self.calculated_data[self.KEY_ACCOUNTS]
        accounts.calculate()

    def _calculate_mapping(self):
        """
        Calculate mapping data

        Update self.calculated_data[self.KEY_ACCOUNTS]
        """
        log.info("### CALCULATE MAPPING ###")
        accounts = self.calculated_data[self.KEY_ACCOUNTS]
        for extension in accounts.list_extensions():
            extension.calculate_mapping(system=accounts.system)

    def save(self):
        """
        Save calculated accounts to output directory
        """
        log.info("### SAVE ACCOUNTS ###")
        self.calculated_data[self.KEY_ACCOUNTS].save_to_path(
            path=self.path_out,
            export_format=self._export_formats_names,
        )
