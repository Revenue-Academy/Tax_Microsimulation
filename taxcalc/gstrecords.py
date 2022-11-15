"""
Tax-Calculator GSTRecords class.
"""
# CODING-STYLE CHECKS:
# pycodestyle records.py
# pylint --disable=locally-disabled records.py

import os
import json
import numpy as np
import pandas as pd
from taxcalc.growfactors import GrowFactors


class GSTRecords(object):
    """
    Constructor for the GST-consumption-unit GSTRecords class.

    Parameters
    ----------
    data: string or Pandas DataFrame
        string describes CSV file in which records data reside;
        DataFrame already contains records data;
        default value is the string 'gst.csv'
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
        default value is filename of the GST weights.

    start_year: integer
        specifies assessment year of the input data;
        default value is GSTCSV_YEAR.
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
    class instance: GSTRecords

    Notes
    -----
    Typical usage when using GST input data is as follows::

        gstrecs =GSTRecords()

    which uses all the default parameters of the constructor, and
    therefore, imputed variables are generated to augment the data and
    initial-year grow factors are applied to the data.  There are
    situations in which you need to specify the values of the GSTRecord
    constructor's arguments, but be sure you know exactly what you are
    doing when attempting this.
    """
    # suppress pylint warnings about unrecognized Records variables:
    # pylint: disable=no-member
    # suppress pylint warnings about uppercase variable names:
    # pylint: disable=invalid-name
    # suppress pylint warnings about too many class instance attributes:
    # pylint: disable=too-many-instance-attributes

    GSTCSV_YEAR = 2017

    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    GST_DATA_FILENAME = 'gst_cmie_august_2020.csv'
    GST_WEIGHTS_FILENAME = 'gst_weights_cmie_august_2020.csv'
    GST_BLOWFACTORS_FILENAME = 'gst_panel_blowup.csv'
    VAR_INFO_FILENAME = 'gstrecords_variables_cmie.json'

    def __init__(self,
                 data=GST_DATA_FILENAME,
                 gfactors=GrowFactors(),
                 weights=GST_WEIGHTS_FILENAME,
                 panel_blowup=GST_BLOWFACTORS_FILENAME,
                 start_year=GSTCSV_YEAR):
        # pylint: disable=too-many-arguments,too-many-locals
        self.__data_year = start_year
        # read specified data
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
        GSTRecords class original data year property.
        """
        return self.__data_year

    @property
    def current_year(self):
        """
        GSTRecords class current assessment year property.
        """
        return self.__current_year

    @property
    def array_length(self):
        """
        Length of arrays in GSTRecords class's DataFrame.
        """
        return self.__dim

    def increment_year(self):
        """
        Add one to current year.
        Also, does extrapolation, reweighting, adjusting for new current year.
        """
        # move to next year
        self.__current_year += 1
        # apply variable extrapolation grow factors
        if self.gfactors is not None:
            self._blowup(self.__current_year)
        # specify current-year sample weights
        if self.WT.size > 0:
            wt_colname = 'WT{}'.format(self.__current_year)
            self.weight = self.WT[wt_colname]

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
        Read Records variables metadata from JSON file;
        returns dictionary and specifies static varname sets listed below.
        """
        var_info_path = os.path.join(GSTRecords.CUR_PATH,
                                     GSTRecords.VAR_INFO_FILENAME)
        if os.path.exists(var_info_path):
            with open(var_info_path) as vfile:
                vardict = json.load(vfile)
        else:
            msg = 'file {} cannot be found'.format(var_info_path)
            raise ValueError(msg)
        GSTRecords.INTEGER_READ_VARS = set(k for k,
                                           v in vardict['read'].items()
                                           if v['type'] == 'int')
        FLOAT_READ_VARS = set(k for k, v in vardict['read'].items()
                              if v['type'] == 'float')
        GSTRecords.MUST_READ_VARS = set(k for k, v in vardict['read'].items()
                                        if v.get('required'))
        GSTRecords.USABLE_READ_VARS = (GSTRecords.INTEGER_READ_VARS |
                                       FLOAT_READ_VARS)
        INT_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                  if v['type'] == 'int')
        FLOAT_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                    if v['type'] == 'float')
        FIXED_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                    if v['type'] == 'unchanging_float')
        GSTRecords.CALCULATED_VARS = (INT_CALCULATED_VARS |
                                      FLOAT_CALCULATED_VARS |
                                      FIXED_CALCULATED_VARS)
        GSTRecords.CHANGING_CALCULATED_VARS = FLOAT_CALCULATED_VARS
        GSTRecords.INTEGER_VARS = (GSTRecords.INTEGER_READ_VARS |
                                   INT_CALCULATED_VARS)
        GSTRecords.FIELD_VARS = list(k for k, v in vardict['read'].items()
                                     if ((v['type'] == 'int') or
                                         (v['type'] == 'float')))
        return vardict

    # specify various sets of variable names
    INTEGER_READ_VARS = None
    MUST_READ_VARS = None
    USABLE_READ_VARS = None
    CALCULATED_VARS = None
    CHANGING_CALCULATED_VARS = None
    INTEGER_VARS = None
    FIELD_VARS = None

    # ----- begin private methods of Records class -----

    def _blowup(self, year):
        """
        Apply to READ (not CALC) variables the grow factors for specified year.
        """
        # pylint: disable=too-many-locals,too-many-statements

        GF_CONSUMPTION = self.gfactors.factor_value('CONSUMPTION', year)
        GF_OTHER = self.gfactors.factor_value('OTHER_CONS_ITEM', year)

        for v in GSTRecords.FIELD_VARS:
            if v.startswith('CONS_') and not(v.startswith('CONS_OTHER')):
                setattr(self, v,
                        getattr(self, v) * GF_CONSUMPTION)
        # self.CONS_OTHER *= GF_OTHER

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
        blowup_path = os.path.join(GSTRecords.CUR_PATH, self.blowfactors_path)
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
        Read GSTRecords data from file or use specified DataFrame as data.
        """
        # pylint: disable=too-many-statements,too-many-branches
        if GSTRecords.INTEGER_VARS is None:
            GSTRecords.read_var_info()
        # read specified data
        if isinstance(data, pd.DataFrame):
            taxdf = data
        elif isinstance(data, str):
            data_path = os.path.join(GSTRecords.CUR_PATH, data)
            if os.path.exists(data_path):
                taxdf = pd.read_csv(data_path)
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
            if varname in GSTRecords.USABLE_READ_VARS:
                READ_VARS.add(varname)
                if varname in GSTRecords.INTEGER_READ_VARS:
                    setattr(self, varname,
                            taxdf[varname].astype(np.int32).values)
                else:
                    setattr(self, varname,
                            taxdf[varname].astype(np.float64).values)
            else:
                self.IGNORED_VARS.add(varname)
        # check that MUST_READ_VARS are all present in taxdf
        if not GSTRecords.MUST_READ_VARS.issubset(READ_VARS):
            msg = 'GSTRecords data missing one or more MUST_READ_VARS'
            raise ValueError(msg)
        # delete intermediate taxdf object
        del taxdf
        # create other class variables that are set to all zeros
        UNREAD_VARS = GSTRecords.USABLE_READ_VARS - READ_VARS
        ZEROED_VARS = GSTRecords.CALCULATED_VARS | UNREAD_VARS
        for varname in ZEROED_VARS:
            if varname in GSTRecords.INTEGER_VARS:
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
        Set to zero all variables in the GSTRecords.CHANGING_CALCULATED_VARS.
        """
        for varname in GSTRecords.CHANGING_CALCULATED_VARS:
            var = getattr(self, varname)
            var.fill(0.)
        del var

    def _read_weights(self, weights):
        """
        Read GSTRecords weights from file or
        use specified DataFrame as data or
        create empty DataFrame if None.
        """
        if weights is None:
            setattr(self, 'WT', pd.DataFrame({'nothing': []}))
            return
        if isinstance(weights, pd.DataFrame):
            WT = weights
        elif isinstance(weights, str):
            weights_path = os.path.join(GSTRecords.CUR_PATH, weights)
            if os.path.isfile(weights_path):
                WT = pd.read_csv(weights_path)
        else:
            msg = 'weights is not None or a string or a Pandas DataFrame'
            raise ValueError(msg)
        assert isinstance(WT, pd.DataFrame)
        setattr(self, 'WT', WT.astype(np.float64))
        del WT
