"""
Tax-Calculator CorpRecords class.
"""
# CODING-STYLE CHECKS:
# pycodestyle records.py
# pylint --disable=locally-disabled records.py

import os
import json
import numpy as np
import pandas as pd
from taxcalc.growfactors import GrowFactors


class CorpRecords(object):
    """
    Constructor for the corporate-tax-filing-unit CorpRecords class.

    Parameters
    ----------
    data: string or Pandas DataFrame
        string describes CSV file in which records data reside;
        DataFrame already contains records data;
        default value is the string 'cit.csv'
        For details on how to use your own data with the Tax-Calculator,
        look at the test_Calculator_using_nonstd_input() function in the
        tests/test_calculate.py file.

    data_type: string of type of data to use;
        May be "cross-section" or "panel"

    gfactors: GrowFactors class instance or None
        containing record data extrapolation (or "blowup") factors.
        NOTE: the constructor should never call the _blowup() method.

    weights: string or Pandas DataFrame or None
        string describes CSV file in which weights reside;
        DataFrame already contains weights;
        None creates empty sample-weights DataFrame;
        default value is filename of the CIT weights.

    start_year: integer
        specifies assessment year of the input data;
        default value is CITCSV_YEAR.
        Note that if specifying your own data (see above) as being a custom
        data set, be sure to explicitly set start_year to the
        custom data's assessment year.

    Raises
    ------
    ValueError:
        if data is not the appropriate type.
        if gfactors is not None or a GrowFactors class instance.
        if start_year is not an integer.
        if files cannot be found.

    Returns
    -------
    class instance: CorpRecords

    Notes
    -----
    Typical usage when using CIT input data is as follows::

        crecs = CorpRecords()

    which uses all the default parameters of the constructor, and
    therefore, imputed variables are generated to augment the data and
    initial-year grow factors are applied to the data.  There are
    situations in which you need to specify the values of the CorpRecord
    constructor's arguments, but be sure you know exactly what you are
    doing when attempting this.
    """
    # suppress pylint warnings about unrecognized Records variables:
    # pylint: disable=no-member
    # suppress pylint warnings about uppercase variable names:
    # pylint: disable=invalid-name
    # suppress pylint warnings about too many class instance attributes:
    # pylint: disable=too-many-instance-attributes

    CITCSV_YEAR = 2017

    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    CIT_DATA_FILENAME = 'cit_cross.csv'
    CIT_WEIGHTS_FILENAME = 'cit_cross_wgts.csv'
    CIT_BLOWFACTORS_FILENAME = 'cit_panel_blowup.csv'
    VAR_INFO_FILENAME = 'corprecords_variables.json'

    def __init__(self,
                 data=CIT_DATA_FILENAME,
                 data_type='cross-section',
                 gfactors=GrowFactors(),
                 weights=CIT_WEIGHTS_FILENAME,
                 panel_blowup=CIT_BLOWFACTORS_FILENAME,
                 start_year=CITCSV_YEAR):
        # pylint: disable=too-many-arguments,too-many-locals
        self.__data_year = start_year
        # read specified data
        if data_type == 'cross-section':
            self.data_type = data_type
        elif data_type == 'panel':
            self.data_type = data_type
            self.blowfactors_path = panel_blowup
        else:
            raise ValueError('data_type is not cross-section or panel')
        self._read_data(data)
        # handle grow factors
        is_correct_type = isinstance(gfactors, GrowFactors)
        if gfactors is not None and not is_correct_type:
            msg = 'gfactors is neither None nor a GrowFactors instance'
            raise ValueError(msg)
        self.gfactors = gfactors
        # read sample weights
        self.WT = None
        self._read_weights(weights)
        # weights must be same size as tax record data
        if self.WT.size > 0 and self.array_length != len(self.WT.index):
            # scale-up sub-sample weights by year-specific factor
            sum_full_weights = self.WT.sum()
            self.WT = self.WT.iloc[self.__index[:len(self.WT.index)]]
            sum_sub_weights = self.WT.sum()
            factor = sum_full_weights / sum_sub_weights
            self.WT *= factor
        # specify current_year and ASSESSMENT_YEAR values
        if isinstance(start_year, int):
            self.__current_year = start_year
            self.ASSESSMENT_YEAR.fill(start_year)
        else:
            msg = 'start_year is not an integer'
            raise ValueError(msg)
        # construct sample weights for current_year
        if self.WT.size > 0:
            wt_colname = 'WT{}'.format(self.current_year)
            if wt_colname in self.WT.columns:
                if len(self.WT[wt_colname]) == self.array_length:
                    self.weight = self.WT[wt_colname]
                else:
                    self.weight = (np.ones(self.array_length) *
                                   sum(self.WT[wt_colname]) /
                                   len(self.WT[wt_colname]))

    @property
    def data_year(self):
        """
        CorpRecords class original data year property.
        """
        return self.__data_year

    @property
    def current_year(self):
        """
        CorpRecords class current assessment year property.
        """
        return self.__current_year

    @property
    def array_length(self):
        """
        Length of arrays in CorpRecords class's DataFrame.
        """
        return self.__dim

    def increment_year(self):
        """
        Add one to current year.
        Also, does extrapolation, reweighting, adjusting for new current year.
        """
        # move to next year
        self.__current_year += 1
        if self.data_type == 'cross-section':
            # apply variable extrapolation grow factors
            if self.gfactors is not None:
                self._blowup(self.__current_year)
        else:
            self.increment_panel_year()
        # specify current-year sample weights
        # weights must be same size as tax record data
        if self.WT.size > 0 and self.array_length != len(self.WT.index):
            # scale-up sub-sample weights by year-specific factor
            sum_full_weights = self.WT.sum()
            self.WT = self.WT.iloc[self.__index[:len(self.WT.index)]]
            sum_sub_weights = self.WT.sum()
            factor = sum_full_weights / sum_sub_weights
            self.WT *= factor
        # construct sample weights for current_year
        if self.WT.size > 0:
            wt_colname = 'WT{}'.format(self.current_year)
            if wt_colname in self.WT.columns:
                if len(self.WT[wt_colname]) == self.array_length:
                    self.weight = self.WT[wt_colname]
                else:
                    self.weight = (np.ones(self.array_length) *
                                   sum(self.WT[wt_colname]) /
                                   len(self.WT[wt_colname]))

    def increment_panel_year(self):
        """
        Add one to current year and to panel year.
        Saves measures to be carried forward.
        Extracts next year of the panel data.
        Updates carried forward measures.
        WARNING: MUST FIX UNIQUE CORPORATE ID FOR MERGING ACROSS YEARS
        """
        # Specify the variables to be carried forward
        carryforward_df = pd.DataFrame({'ID_NO': self.ID_NO,
                                        'newloss1': self.newloss1,
                                        'newloss2': self.newloss2,
                                        'newloss3': self.newloss3,
                                        'newloss4': self.newloss4,
                                        'newloss5': self.newloss5,
                                        'newloss6': self.newloss6,
                                        'newloss7': self.newloss7,
                                        'newloss8': self.newloss8,
                                        'close_wdv_pm1': self.close_wdv_pm1})
        # Update years
        self.panelyear += 1
        # Get new panel data
        data1 = self._extract_panel_year()
        data2 = data1.merge(right=carryforward_df, how='outer',
                            on='ID_NO', indicator=True)
        merge_info = np.array(data2['_merge'])
        to_update = np.where(merge_info == 'both', True, False)
        to_keep = np.where(merge_info != 'right_only', True, False)
        data2['LOSS_LAG1'] = np.where(to_update, data2['newloss1'],
                                      data2['LOSS_LAG1'])
        data2['LOSS_LAG2'] = np.where(to_update, data2['newloss2'],
                                      data2['LOSS_LAG2'])
        data2['LOSS_LAG3'] = np.where(to_update, data2['newloss3'],
                                      data2['LOSS_LAG3'])
        data2['LOSS_LAG4'] = np.where(to_update, data2['newloss4'],
                                      data2['LOSS_LAG4'])
        data2['LOSS_LAG5'] = np.where(to_update, data2['newloss5'],
                                      data2['LOSS_LAG5'])
        data2['LOSS_LAG6'] = np.where(to_update, data2['newloss6'],
                                      data2['LOSS_LAG6'])
        data2['LOSS_LAG7'] = np.where(to_update, data2['newloss7'],
                                      data2['LOSS_LAG7'])
        data2['LOSS_LAG8'] = np.where(to_update, data2['newloss8'],
                                      data2['LOSS_LAG8'])
        temp = np.where(to_update, data2['close_wdv_pm1'],
                        data2['PWR_DOWN_VAL_1ST_DAY_PY_15P'])
        data2['PWR_DOWN_VAL_1ST_DAY_PY_15P'] = temp
        data3 = data2[to_keep]
        self._read_data(data3)

    def set_current_year(self, new_current_year):
        """
        Set current year to specified value and updates ASSESSMENT_YEAR
        variable.
        Unlike increment_year method, extrapolation, reweighting, adjusting
        are skipped.
        """
        self.__current_year = new_current_year
        self.ASSESSMENT_YEAR.fill(new_current_year)

    @staticmethod
    def read_var_info():
        """
        Read CorpRecords variables metadata from JSON file;
        returns dictionary and specifies static varname sets listed below.
        """
        var_info_path = os.path.join(CorpRecords.CUR_PATH,
                                     CorpRecords.VAR_INFO_FILENAME)
        if os.path.exists(var_info_path):
            with open(var_info_path) as vfile:
                vardict = json.load(vfile)
        else:
            msg = 'file {} cannot be found'.format(var_info_path)
            raise ValueError(msg)
        CorpRecords.INTEGER_READ_VARS = set(k for k,
                                            v in vardict['read'].items()
                                            if v['type'] == 'int')
        FLOAT_READ_VARS = set(k for k, v in vardict['read'].items()
                              if v['type'] == 'float')
        CorpRecords.MUST_READ_VARS = set(k for k, v in vardict['read'].items()
                                         if v.get('required'))
        CorpRecords.USABLE_READ_VARS = (CorpRecords.INTEGER_READ_VARS |
                                        FLOAT_READ_VARS)
        INT_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                  if v['type'] == 'int')
        FLOAT_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                    if v['type'] == 'float')
        FIXED_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                    if v['type'] == 'unchanging_float')
        CorpRecords.CALCULATED_VARS = (INT_CALCULATED_VARS |
                                       FLOAT_CALCULATED_VARS |
                                       FIXED_CALCULATED_VARS)
        CorpRecords.CHANGING_CALCULATED_VARS = FLOAT_CALCULATED_VARS
        CorpRecords.INTEGER_VARS = (CorpRecords.INTEGER_READ_VARS |
                                    INT_CALCULATED_VARS)
        return vardict

    # specify various sets of variable names
    INTEGER_READ_VARS = None
    MUST_READ_VARS = None
    USABLE_READ_VARS = None
    CALCULATED_VARS = None
    CHANGING_CALCULATED_VARS = None
    INTEGER_VARS = None

    # ----- begin private methods of Records class -----

    def _blowup(self, year):
        """
        Apply to READ (not CALC) variables the grow factors for specified year.
        """
        # pylint: disable=too-many-locals,too-many-statements
        GF_CORP1 = self.gfactors.factor_value('CORP', year)
        GF_RENT = self.gfactors.factor_value('RENT', year)
        GF_BP_NONSPECULATIVE = self.gfactors.factor_value('BP_NONSPECULATIVE',
                                                          year)
        GF_BP_SPECULATIVE = self.gfactors.factor_value('BP_SPECULATIVE',
                                                       year)
        GF_BP_SPECIFIED = self.gfactors.factor_value('BP_SPECIFIED', year)
        GF_BP_PATENT115BBF = self.gfactors.factor_value('BP_PATENT115BBF',
                                                        year)
        GF_ST_CG_AMT_1 = self.gfactors.factor_value('ST_CG_AMT_1', year)
        GF_ST_CG_AMT_2 = self.gfactors.factor_value('ST_CG_AMT_2', year)
        GF_LT_CG_AMT_1 = self.gfactors.factor_value('LT_CG_AMT_1', year)
        GF_LT_CG_AMT_2 = self.gfactors.factor_value('LT_CG_AMT_2', year)
        GF_STCG_APPRATE = self.gfactors.factor_value('STCG_APPRATE', year)
        GF_OINCOME = self.gfactors.factor_value('OINCOME', year)
        GF_CYL_SET_OFF = self.gfactors.factor_value('LOSSES_CY', year)
        GF_DEDUCTIONS = self.gfactors.factor_value('DEDUCTIONS', year)
        GF_DEDUCTION_10AA = self.gfactors.factor_value('DEDU_SEC_10A_OR_10AA',
                                                       year)
        GF_NET_AGRC_INCOME = self.gfactors.factor_value('AGRI_INCOME', year)
        GF_INVESTMENT = self.gfactors.factor_value('INVESTMENT', year)
        self.ST_CG_AMT_1 *= GF_ST_CG_AMT_1
        self.ST_CG_AMT_2 *= GF_ST_CG_AMT_2
        self.ST_CG_AMT_APPRATE *= GF_STCG_APPRATE
        self.LT_CG_AMT_1 *= GF_LT_CG_AMT_1
        self.LT_CG_AMT_2 *= GF_LT_CG_AMT_2
        self.INCOME_HP *= GF_RENT
        self.PRFT_GAIN_BP_OTHR_SPECLTV_BUS *= GF_BP_NONSPECULATIVE
        self.PRFT_GAIN_BP_SPECLTV_BUS *= GF_BP_SPECULATIVE
        self.PRFT_GAIN_BP_SPCFD_BUS *= GF_BP_SPECIFIED
        self.PRFT_GAIN_BP_INC_115BBF *= GF_BP_PATENT115BBF
        self.TOTAL_INCOME_OS *= GF_OINCOME
        self.CYL_SET_OFF *= GF_CYL_SET_OFF
        self.TOTAL_DEDUC_VIA *= GF_DEDUCTIONS
        self.TOTAL_DEDUC_10AA *= GF_DEDUCTION_10AA
        self.NET_AGRC_INCOME *= GF_NET_AGRC_INCOME
        self.PWR_DOWN_VAL_1ST_DAY_PY_15P *= GF_INVESTMENT
        self.PADDTNS_180_DAYS__MOR_PY_15P *= GF_INVESTMENT
        self.PCR34_PY_15P *= GF_INVESTMENT
        self.PADDTNS_LESS_180_DAYS_15P *= GF_INVESTMENT
        self.PCR7_PY_15P *= GF_INVESTMENT
        self.PEXP_INCURRD_TRF_ASSTS_15P *= GF_INVESTMENT
        self.PCAP_GAINS_LOSS_SEC50_15P *= GF_INVESTMENT

    def _extract_panel_year(self):
        """
        Reads the panel data and extracts observations for the given panelyear.
        Then applies the specified blowup factors to advance the panel data
        to the appropriate year.
        This assumes that the full panel data has already been read and stored
        in self.full_panel.
        The blowup factors are applies to READ (not CALC) variables.
        """
        # read in the blow-up factors
        blowup_path = os.path.join(CorpRecords.CUR_PATH, self.blowfactors_path)
        blowup_data_all = pd.read_csv(blowup_path, index_col='YEAR')
        blowup_data = blowup_data_all.loc[self.panelyear + 4]
        # extract the observations for the intended year
        assessyear = np.array(self.full_panel['ASSESSMENT_YEAR'])
        data1 = self.full_panel[assessyear == self.panelyear].reset_index()
        # apply the blowup factors
        BF_CORP1 = blowup_data['AGGREGATE_LIABILTY']
        BF_RENT = blowup_data['INCOME_HP']
        BF_BP_NONSPECULAT = blowup_data['PRFT_GAIN_BP_OTHR_SPECLTV_BUS']
        BF_BP_SPECULATIVE = blowup_data['PRFT_GAIN_BP_SPECLTV_BUS']
        BF_BP_SPECIFIED = blowup_data['PRFT_GAIN_BP_SPCFD_BUS']
        BF_BP_PATENT115BBF = blowup_data['AGGREGATE_LIABILTY']
        BF_ST_CG_AMT_1 = blowup_data['ST_CG_AMT_1']
        BF_ST_CG_AMT_2 = blowup_data['ST_CG_AMT_2']
        BF_LT_CG_AMT_1 = blowup_data['LT_CG_AMT_1']
        BF_LT_CG_AMT_2 = blowup_data['LT_CG_AMT_2']
        BF_STCG_APPRATE = blowup_data['ST_CG_AMT_APPRATE']
        BF_OINCOME = blowup_data['TOTAL_INCOME_OS']
        BF_CYL_SET_OFF = blowup_data['CYL_SET_OFF']
        BF_DEDUCTIONS = blowup_data['TOTAL_DEDUC_VIA']
        BF_DEDUCTION_10AA = blowup_data['DEDUCT_SEC_10A_OR_10AA']
        BF_NET_AGRC_INC = blowup_data['NET_AGRC_INCOME']
        BF_INVESTMENT = blowup_data['INVESTMENT']
        # Apply blow-up factors
        data1['INCOME_HP'] = data1['INCOME_HP'] * BF_RENT
        temp = data1['PRFT_GAIN_BP_OTHR_SPECLTV_BUS']
        data1['PRFT_GAIN_BP_OTHR_SPECLTV_BUS'] = temp * BF_BP_NONSPECULAT
        temp = data1['PRFT_GAIN_BP_SPECLTV_BUS']
        data1['PRFT_GAIN_BP_SPECLTV_BUS'] = temp * BF_BP_SPECULATIVE
        data1['PRFT_GAIN_BP_SPCFD_BUS'] = (data1['PRFT_GAIN_BP_SPCFD_BUS'] *
                                           BF_BP_SPECIFIED)
        data1['TOTAL_INCOME_OS'] = data1['TOTAL_INCOME_OS'] * BF_OINCOME
        data1['ST_CG_AMT_1'] = data1['ST_CG_AMT_1'] * BF_ST_CG_AMT_1
        data1['ST_CG_AMT_2'] = data1['ST_CG_AMT_2'] * BF_ST_CG_AMT_2
        data1['LT_CG_AMT_1'] = data1['LT_CG_AMT_1'] * BF_LT_CG_AMT_1
        data1['LT_CG_AMT_2'] = data1['LT_CG_AMT_2'] * BF_LT_CG_AMT_2
        data1['ST_CG_AMT_APPRATE'] = (data1['ST_CG_AMT_APPRATE'] *
                                      BF_STCG_APPRATE)
        data1['CYL_SET_OFF'] = data1['CYL_SET_OFF'] * BF_CYL_SET_OFF
        data1['TOTAL_DEDUC_VIA'] = data1['TOTAL_DEDUC_VIA'] * BF_DEDUCTIONS
        data1['NET_AGRC_INCOME'] = data1['NET_AGRC_INCOME'] * BF_NET_AGRC_INC
        temp = data1['PWR_DOWN_VAL_1ST_DAY_PY_15P']
        data1['PWR_DOWN_VAL_1ST_DAY_PY_15P'] = temp * BF_INVESTMENT
        temp = data1['PADDTNS_180_DAYS__MOR_PY_15P']
        data1['PADDTNS_180_DAYS__MOR_PY_15P'] = temp * BF_INVESTMENT
        temp = data1['PCR34_PY_15P']
        data1['PCR34_PY_15P'] = temp * BF_INVESTMENT
        temp = data1['PADDTNS_LESS_180_DAYS_15P']
        data1['PADDTNS_LESS_180_DAYS_15P'] = temp * BF_INVESTMENT
        temp = data1['PCR7_PY_15P']
        data1['PCR7_PY_15P'] = temp * BF_INVESTMENT
        temp = data1['PEXP_INCURRD_TRF_ASSTS_15P']
        data1['PEXP_INCURRD_TRF_ASSTS_15P'] = temp * BF_INVESTMENT
        temp = data1['PCAP_GAINS_LOSS_SEC50_15P']
        data1['PCAP_GAINS_LOSS_SEC50_15P'] = temp * BF_INVESTMENT
        # Handle potential missing variables
        if 'PRFT_GAIN_BP_INC_115BBF' in list(data1):
            temp = data1['PRFT_GAIN_BP_INC_115BBF']
            data1['PRFT_GAIN_BP_INC_115BBF'] = temp * BF_BP_PATENT115BBF
        if 'TOTAL_DEDUC_10AA' in list(data1):
            temp = data1['TOTAL_DEDUC_10AA']
            data1['TOTAL_DEDUC_10AA'] = temp * BF_DEDUCTION_10AA
        return data1

    def _read_data(self, data):
        """
        Read CorpRecords data from file or use specified DataFrame as data.
        """
        # pylint: disable=too-many-statements,too-many-branches
        if CorpRecords.INTEGER_VARS is None:
            CorpRecords.read_var_info()
        # read specified data
        if isinstance(data, pd.DataFrame):
            if self.data_type == 'cross-section':
                taxdf = data
            else:
                try:
                    # If receiving the next year's data
                    self.panelyear
                    taxdf = data
                except AttributeError:
                    # New CorpRecords object, using full panel
                    self.full_panel = data
                    assessyear = np.array(self.full_panel['ASSESSMENT_YEAR'])
                    self.panelyear = min(assessyear)
                    taxdf = self._extract_panel_year()
        elif isinstance(data, str):
            data_path = os.path.join(CorpRecords.CUR_PATH, data)
            if os.path.exists(data_path):
                if self.data_type == 'cross-section':
                    taxdf = pd.read_csv(data_path)
                else:
                    # Read in the full panel data (all years)
                    self.full_panel = pd.read_csv(data_path)
                    assessyear = np.array(self.full_panel['ASSESSMENT_YEAR'])
                    self.panelyear = min(assessyear)
                    taxdf = self._extract_panel_year()
            else:
                msg = 'file {} cannot be found'.format(data_path)
                raise ValueError(msg)
        else:
            msg = 'data is neither a string nor a Pandas DataFrame'
            raise ValueError(msg)
        self.__dim = len(taxdf.index)
        self.__index = taxdf.index
        # create class variables using taxdf column names
        READ_VARS = set()
        self.IGNORED_VARS = set()
        for varname in list(taxdf.columns.values):
            if varname in CorpRecords.USABLE_READ_VARS:
                READ_VARS.add(varname)
                if varname in CorpRecords.INTEGER_READ_VARS:
                    setattr(self, varname,
                            taxdf[varname].astype(np.int32).values)
                else:
                    setattr(self, varname,
                            taxdf[varname].astype(np.float64).values)
            else:
                self.IGNORED_VARS.add(varname)
        # check that MUST_READ_VARS are all present in taxdf
        if not CorpRecords.MUST_READ_VARS.issubset(READ_VARS):
            msg = 'CorpRecords data missing one or more MUST_READ_VARS'
            raise ValueError(msg)
        # delete intermediate taxdf object
        del taxdf
        # create other class variables that are set to all zeros
        UNREAD_VARS = CorpRecords.USABLE_READ_VARS - READ_VARS
        ZEROED_VARS = CorpRecords.CALCULATED_VARS | UNREAD_VARS
        for varname in ZEROED_VARS:
            if varname in CorpRecords.INTEGER_VARS:
                setattr(self, varname,
                        np.zeros(self.array_length, dtype=np.int32))
            else:
                setattr(self, varname,
                        np.zeros(self.array_length, dtype=np.float64))
        # delete intermediate variables
        del READ_VARS
        del UNREAD_VARS
        del ZEROED_VARS

    def zero_out_changing_calculated_vars(self):
        """
        Set to zero all variables in the CorpRecords.CHANGING_CALCULATED_VARS.
        """
        for varname in CorpRecords.CHANGING_CALCULATED_VARS:
            var = getattr(self, varname)
            var.fill(0.)
        del var

    def _read_weights(self, weights):
        """
        Read CorpRecords weights from file or
        use specified DataFrame as data or
        create empty DataFrame if None.
        """
        if weights is None:
            setattr(self, 'WT', pd.DataFrame({'nothing': []}))
            return
        if isinstance(weights, pd.DataFrame):
            WT = weights
        elif isinstance(weights, str):
            weights_path = os.path.join(CorpRecords.CUR_PATH, weights)
            if os.path.isfile(weights_path):
                WT = pd.read_csv(weights_path)
        else:
            msg = 'weights is not None or a string or a Pandas DataFrame'
            raise ValueError(msg)
        assert isinstance(WT, pd.DataFrame)
        setattr(self, 'WT', WT.astype(np.float64))
        del WT
