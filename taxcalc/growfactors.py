"""
Tax-Calculator GrowFactors class.
"""
# CODING-STYLE CHECKS:
# pycodestyle growfactors.py
# pylint --disable=locally-disabled growfactors.py

import os
import json
import numpy as np
import pandas as pd
from taxcalc.utils import read_egg_csv


class GrowFactors(object):
    """
    Constructor for the GrowFactors class.

    Parameters
    ----------
    growfactors_filename: string
        string is name of CSV file in which grow factors reside;
        default value is name of file containing baseline grow factors.

    Raises
    ------
    ValueError:
        if growfactors_filename is not a string.

    Returns
    -------
    class instance: GrowFactors

    Notes
    -----
    Typical usage is "gfactor = GrowFactors()", which produces an object
    containing the default grow factors in the GrowFactors.FILENAME file.
    """

    # f = open('global_vars.json')
    # vars = json.load(f)
    # print("vars in growfactors", vars)

    # GROWFACTORS_FILENAME = vars['GROWFACTORS_FILENAME']
    
    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    FILENAME = 'growfactors_new.csv'
    FILE_PATH = os.path.join(CUR_PATH, FILENAME)

    # TODO: Growfactors for Corporate and non-corporate Income heads are
    # TODO: currently set as same. New field names should be read in case we
    # TODO: want separate growfactors for Corporate and Non-corporate data.
    # f = open(os.path.join(CUR_PATH, vars['records_variables_filename']))
    # records_variables = json.load(f)
    # f = open(os.path.join(CUR_PATH, vars['corprecords_variables_filename']))
    # corprecords_variables = json.load(f)
    # f = open(os.path.join(CUR_PATH, vars['gstrecords_variables_filename']))
    # gstrecords_variables = json.load(f)

    # set1 = set(records_variables['read'].keys())
    # set2 = set(corprecords_variables['read'].keys())
    # set3 = set(gstrecords_variables['read'].keys()) 
    # set4 = set(['CPI'])
    # set5 = set(['CONSUMPTION', 'OTHER_CONS_ITEM'])
    # VALID_NAMES = set.union(set1, set2, set3, set4, set5)
    
    VALID_NAMES = set(['CPI', 'SALARY', 'INCOME_HP', 'PRFT_GAIN_BP_OTHR_SPECLTV_BUS', 'PRFT_GAIN_BP_SPECLTV_BUS', 
    'PRFT_GAIN_BP_SPCFD_BUS',	'ST_CG_AMT_1', 'ST_CG_AMT_2', 'ST_CG_AMT_APPRATE', 
    'LT_CG_AMT_1', 'LT_CG_AMT_2', 'TOTAL_INCOME_OS', 'CY_Losses', 'DEDUCT_SEC_10A_OR_10AA', 
    'TOTAL_DEDUC_VIA', 'CRDT_SEC_115JAA_TAX_PAID_EYRS', 'RELIEF_90', 
    'RELIEF_91', 'DEEMED_TI_SEC115JB', 'PADDTNS_180_DAYS__MOR_PY_15P', 'PADDTNS_180_DAYS__MOR_PY_30P', 
    'PADDTNS_180_DAYS__MOR_PY_40P', 'PADDTNS_180_DAYS__MOR_PY_50P', 'PADDTNS_180_DAYS__MOR_PY_60P',
    'PADDTNS_180_DAYS__MOR_PY_80P', 'PADDTNS_180_DAYS__MOR_PY_100P', 'PADDTNS_LESS_180_DAYS_15P', 
    'PADDTNS_LESS_180_DAYS_30P', 'PADDTNS_LESS_180_DAYS_40P',
    'PADDTNS_LESS_180_DAYS_50P', 'PADDTNS_LESS_180_DAYS_60P', 'PADDTNS_LESS_180_DAYS_80P',
    'PADDTNL_DEPRECTN_ANY_4_15P', 'PADDTNL_DEPRECTN_ANY_4_30P', 'PADDTNL_DEPRECTN_ANY_4_40P',
    'PADDTNL_DEPRECTN_ANY_4_50P', 'PADDTNL_DEPRECTN_ANY_4_60P', 'PADDTNL_DEPRECTN_ANY_4_80P', 
    'PADDTNL_DEPRECTN_ANY_4_100P', 'PADDTNL_DEPRECTN_ANY_7_15P', 'PADDTNL_DEPRECTN_ANY_7_30P',
    'PADDTNL_DEPRECTN_ANY_7_40P', 'PADDTNL_DEPRECTN_ANY_7_50P', 'PADDTNL_DEPRECTN_ANY_7_60P',
    'PADDTNL_DEPRECTN_ANY_7_80P', 'PADDTNL_DEPRECTN_ANY_7_100P', 'PWR_DOWN_VAL_1ST_DAY_PY_15P', 
    'PWR_DOWN_VAL_1ST_DAY_PY_30P', 'PWR_DOWN_VAL_1ST_DAY_PY_40P', 'PWR_DOWN_VAL_1ST_DAY_PY_50P',
    'PWR_DOWN_VAL_1ST_DAY_PY_60P', 'PWR_DOWN_VAL_1ST_DAY_PY_80P', 'PWR_DOWN_VAL_1ST_DAY_PY_100P',
    'PCR34_PY_15P', 'PCR34_PY_30P', 'PCR34_PY_40P', 'PCR34_PY_50P', 'PCR34_PY_60P', 'PCR34_PY_80P',
    'PCR34_PY_100P', 'PCR7_PY_15P', 'PCR7_PY_30P', 'PCR7_PY_40P', 'PCR7_PY_50P', 'PCR7_PY_60P', 
    'PCR7_PY_80P', 'PCR7_PY_100P', 'PEXP_INCURRD_TRF_ASSTS_15P', 
    'PEXP_INCURRD_TRF_ASSTS_30P', 'PEXP_INCURRD_TRF_ASSTS_40P', 'PEXP_INCURRD_TRF_ASSTS_50P', 
    'PEXP_INCURRD_TRF_ASSTS_60P', 'PEXP_INCURRD_TRF_ASSTS_80P', 'PEXP_INCURRD_TRF_ASSTS_100P', 
    'PCAP_GAINS_LOSS_SEC50_15P', 'PCAP_GAINS_LOSS_SEC50_30P', 'PCAP_GAINS_LOSS_SEC50_40P', 
    'PCAP_GAINS_LOSS_SEC50_50P', 'PCAP_GAINS_LOSS_SEC50_60P', 'PCAP_GAINS_LOSS_SEC50_80P', 
    'PCAP_GAINS_LOSS_SEC50_100P'])

    def __init__(self, growfactors_filename=FILE_PATH):
        # read grow factors from specified growfactors_filename
        gfdf = pd.DataFrame()
        CUR_PATH = os.path.abspath(os.path.dirname(__file__))
        #FILENAME = 'growfactors.csv'
        growfactors_filepath = os.path.join(CUR_PATH, growfactors_filename)
        if isinstance(growfactors_filepath, str):
            if os.path.isfile(growfactors_filepath):
                gfdf = pd.read_csv(growfactors_filepath,
                                   index_col='YEAR')
            else:
                # cannot call read_egg_ function in unit tests
                gfdf = read_egg_csv(GrowFactors.GROWFACTORS_FILENAME,
                                    index_col='YEAR')  # pragma: no cover
        else:
            raise ValueError('growfactors_filename is not a string')
        assert isinstance(gfdf, pd.DataFrame)
        # check validity of gfdf column names
        gfdf_names = set(list(gfdf))
        #print(GrowFactors.GROWFACTORS_FILENAME)
        #print("gfdf_names: ", gfdf_names)
        #print("GrowFactors.VALID_NAMES: ", GrowFactors.VALID_NAMES)
        if not gfdf_names.issubset(GrowFactors.VALID_NAMES):
        #if gfdf_names != GrowFactors.VALID_NAMES:
            msg = ('missing names are: {} and invalid names are: {}')
            missing = GrowFactors.VALID_NAMES - gfdf_names
            invalid = gfdf_names - GrowFactors.VALID_NAMES
            raise ValueError(msg.format(missing, invalid))
        # determine first_year and last_year from gfdf
        self._first_year = min(gfdf.index)
        self._last_year = max(gfdf.index)
        # set gfdf as attribute of class
        self.gfdf = pd.DataFrame()
        setattr(self, 'gfdf',
                gfdf.astype(np.float64))  # pylint: disable=no-member
        del gfdf
        # specify factors as being unused (that is, not yet accessed)
        self.used = False

    @property
    def first_year(self):
        """
        GrowFactors class start_year property.
        """
        return self._first_year

    @property
    def last_year(self):
        """
        GrowFactors class last_year property.
        """
        return self._last_year

    def price_inflation_rates(self, firstyear, lastyear):
        """
        Return list of price inflation rates rounded to four decimal digits.
        """
        self.used = True
        if firstyear > lastyear:
            msg = 'first_year={} > last_year={}'
            raise ValueError(msg.format(firstyear, lastyear))
        if firstyear < self.first_year:
            msg = 'firstyear={} < GrowFactors.first_year={}'
            raise ValueError(msg.format(firstyear, self.first_year))
        if lastyear > self.last_year:
            msg = 'last_year={} > GrowFactors.last_year={}'
            raise ValueError(msg.format(lastyear, self.last_year))
        # pylint: disable=no-member
        rates = [round((self.gfdf['CPI'][cyr] - 1.0), 4)
                 for cyr in range(firstyear, lastyear + 1)]
        return rates

    def wage_growth_rates(self, firstyear, lastyear):
        """
        Return list of wage growth rates rounded to four decimal digits.
        """
        self.used = True
        if firstyear > lastyear:
            msg = 'firstyear={} > lastyear={}'
            raise ValueError(msg.format(firstyear, lastyear))
        if firstyear < self.first_year:
            msg = 'firstyear={} < GrowFactors.first_year={}'
            raise ValueError(msg.format(firstyear, self.first_year))
        if lastyear > self.last_year:
            msg = 'lastyear={} > GrowFactors.last_year={}'
            raise ValueError(msg.format(lastyear, self.last_year))
        # pylint: disable=no-member
        rates = [round((self.gfdf['SALARY'][cyr] - 1.0), 4)
                 for cyr in range(firstyear, lastyear + 1)]
        return rates

    def factor_value(self, name, year):
        """
        Return value of factor with specified name for specified year.
        """
        self.used = True
        if name not in GrowFactors.VALID_NAMES:
            msg = 'name={} not in GrowFactors.VALID_NAMES'
            raise ValueError(msg.format(year, name))
        if year < self.first_year:
            msg = 'year={} < GrowFactors.first_year={}'
            raise ValueError(msg.format(year, self.first_year))
        if year > self.last_year:
            msg = 'year={} > GrowFactors.last_year={}'
            raise ValueError(msg.format(year, self.last_year))
        return self.gfdf[name][year]

    def factor_names(self):
        """
        Return value of factor with specified name for specified year.
        """
        self.used = True
        return set(self.gfdf.columns)