"""
pitaxcalc-demo functions that calculate personal income tax liability.
"""
# CODING-STYLE CHECKS:
# pycodestyle functions.py
# pylint --disable=locally-disabled functions.py

import math
import copy
import numpy as np
from taxcalc.decorators import iterate_jit



@iterate_jit(nopython=True)
def net_salary_income(SALARIES, std_deduction, Income_Salary):
    """
    Compute net salary as gross salary minus deductions u/s 16.
    """
    # TODO: when gross salary and deductions are avaiable, do the calculation
    # TODO: when using net_salary as function argument, no calculations neeed
    """
    The deductions (transport and medical) that are being done away with while
    intrducing Standard Deduction is not captured in the schedule also. Thus,
    the two deductions combined (crude estimate gives a figure of 30000) is
    added to "SALARIES" and then "std_deduction" (introduced as a policy
    variable) is deducted to get "Income_Salary". Standard Deduction is being
    intruduced only from AY 2019 onwards, "std_deduction" is set as 30000 for
    AY 2017 and of 2018 thus resulting in no change for those years.
    """
    Income_Salary = SALARIES + 30000
    if Income_Salary <= std_deduction:
        Income_Salary = 0
    else:
        Income_Salary -= std_deduction
    return Income_Salary


@iterate_jit(nopython=True)
def net_rental_income(INCOME_HP):
    """
    Compute house-property rental income net of taxes, depreciation, and
    mortgage interest.
    """
    # TODO: when gross rental income and taxes, depreciation, and interest
    #       are available, do the calculation
    # TODO: when using net_rent as function argument, no calculations neeed
    return INCOME_HP


@iterate_jit(nopython=True)
def income_business_profession(PRFT_GAIN_BP_OTHR_SPECLTV_BUS,
                               PRFT_GAIN_BP_SPECLTV_BUS,
                               PRFT_GAIN_BP_SPCFD_BUS,
                               PRFT_GAIN_BP_INC_115BBF, Income_BP):
    """
    Compute Income from Business and Profession by adding the different
    sub-heads (i.e speculative, non-speculative, specified, patents, etc)
    """
    # TODO: when reading from schedule BP, calculate Income_BP from the read
    # TODO: variables of the schedule
    Income_BP = (PRFT_GAIN_BP_OTHR_SPECLTV_BUS + PRFT_GAIN_BP_SPECLTV_BUS +
                 PRFT_GAIN_BP_SPCFD_BUS + PRFT_GAIN_BP_INC_115BBF)
    return Income_BP


@iterate_jit(nopython=True)
def total_other_income(TOTAL_INCOME_OS):
    """
    Compute other_income from its components.
    """
    # TODO: when components of other income are available, do the calculation
    # TODO: when using other_income as function argument, no calculations neeed
    return TOTAL_INCOME_OS


@iterate_jit(nopython=True)
def current_year_losses(CYL_SET_OFF, CY_Losses):
    """
    Compute Current Year Losses to be set off, from Schedule CYLA.
    """
    # TODO: when schedule is available, do the calculation
    # TODO: when reading CYL_SET_OFF from the data, no calculations neeed
    CY_Losses = CYL_SET_OFF
    return CY_Losses


@iterate_jit(nopython=True)
def brought_fwd_losses(BFL_SET_OFF_BALANCE, BF_Losses):
    """
    Compute Brought forward Losses to be set off, from Schedule BFLA.
    """
    # TODO: when schedule is available, do the calculation
    # TODO: when reading BFL_SET_OFF_BALANCE from the data, no calculations
    BF_Losses = BFL_SET_OFF_BALANCE
    return BF_Losses


@iterate_jit(nopython=True)
def agri_income(Income_Rate_Purpose, NET_AGRC_INCOME):
    """
    Compute the total Income that is used for rate purpose.
    It currently has only the net agricultural income.
    """
    # TODO: when shedule is available, do the calculation
    Income_Rate_Purpose = NET_AGRC_INCOME
    return Income_Rate_Purpose


@iterate_jit(nopython=True)
def gross_total_income(Income_Salary, INCOME_HP, Income_BP, ST_CG_AMT_1,
                       ST_CG_AMT_2, ST_CG_AMT_APPRATE, LT_CG_AMT_1,
                       LT_CG_AMT_2, TOTAL_INCOME_OS, CY_Losses, BF_Losses,
                       GTI):
    """
    Compute GTI including capital gains amounts taxed at special rates.
    """
    GTI = (Income_Salary + INCOME_HP + Income_BP + ST_CG_AMT_1 + ST_CG_AMT_2 +
           ST_CG_AMT_APPRATE + LT_CG_AMT_1 + LT_CG_AMT_2 +
           TOTAL_INCOME_OS) - (CY_Losses + BF_Losses)
    GTI = np.maximum(0., GTI)
    return GTI


@iterate_jit(nopython=True)
def itemized_deductions(deductions, TOTAL_DEDUC_VIA):
    """
    Compute deductions from itemizeable expenses and caps.
    """
    # TODO: when expenses and caps policy are available, do the calculation
    # TODO: when using deductions as function argument, no calculations neeed
    deductions = TOTAL_DEDUC_VIA
    return deductions


@iterate_jit(nopython=True)
def deduction_10AA(deduction_10AA, TOTAL_DEDUC_10AA):
    """
    Compute deductions from itemizeable expenses and caps.
    """
    # TODO: when expenses and caps policy are available, do the calculation
    # TODO: when using deductions as function argument, no calculations neeed
    deduction_10AA = TOTAL_DEDUC_10AA
    return deduction_10AA


@iterate_jit(nopython=True)
def taxable_total_income(GTI, deductions, TTI):
    """
    Compute TTI.
    """
    TTI = GTI - deductions
    TTI = np.maximum(0., TTI)
    return TTI


@iterate_jit(nopython=True)
def tax_stcg_splrate(ST_CG_RATE1, ST_CG_RATE2, ST_CG_AMT_1, ST_CG_AMT_2):
    """
    Calculates the tax on short term capital gains which are taxed at spl rate
    Short term capital gain tax at applicable rate is included in tax on GTI.
    """
    Tax_ST_CG_RATE1 = ST_CG_AMT_1 * ST_CG_RATE1
    Tax_ST_CG_RATE2 = ST_CG_AMT_2 * ST_CG_RATE2
    Total_Tax_STCG = Tax_ST_CG_RATE1 + Tax_ST_CG_RATE2
    return (Tax_ST_CG_RATE1, Tax_ST_CG_RATE2, Total_Tax_STCG)


@iterate_jit(nopython=True)
def tax_ltcg_splrate(LT_CG_RATE1, LT_CG_RATE2, LT_CG_AMT_1, LT_CG_AMT_2):
    """
    Calculates the tax on long term capital gains which are taxed at spl rates
    """
    Tax_LT_CG_RATE1 = LT_CG_AMT_1 * LT_CG_RATE1
    Tax_LT_CG_RATE2 = LT_CG_AMT_2 * LT_CG_RATE2
    Total_Tax_LTCG = Tax_LT_CG_RATE1 + Tax_LT_CG_RATE2
    return (Tax_LT_CG_RATE1, Tax_LT_CG_RATE2, Total_Tax_LTCG)


@iterate_jit(nopython=True)
def tax_specialrates(ST_CG_AMT_1, ST_CG_AMT_2, LT_CG_AMT_1, LT_CG_AMT_2,
                     Total_Tax_STCG, Total_Tax_LTCG):
    """
    Calculates the total capital gains and tax on it
    which are taxed at spl rates
    """
    TI_special_rates = ST_CG_AMT_1 + ST_CG_AMT_2 + LT_CG_AMT_1 + LT_CG_AMT_2
    tax_TI_special_rates = Total_Tax_STCG + Total_Tax_LTCG
    return (TI_special_rates, tax_TI_special_rates)


DEBUG = False
DEBUG_IDX = 0


@iterate_jit(nopython=True)
def pit_liability(rate1, rate2, rate3, rate4, tbrk1, tbrk2, tbrk3, tbrk4,
                  rebate_rate, rebate_thd, rebate_ceiling,
                  surcharge_rate, surcharge_thd, cess_rate,
                  TTI, TI_special_rates, tax_TI_special_rates,
                  Income_Rate_Purpose, AGEGRP, Total_Tax_Cap_Gains,
                  Total_Tax_STCG, Total_Tax_LTCG,
                  Aggregate_Income, tax_Aggregate_Income, rebate_agri,
                  tax_TTI, rebate, surcharge, cess, pitax):
    """
    Compute tax liability given the progressive tax rate schedule specified
    by the (marginal tax) rate* and (upper tax bracket) brk* parameters and
    given taxable income (taxinc)

    Subtract 'TI_special_rates' from 'TTI' to get the portion of total income
    that is taxed at normal rates. Now add agricultural income (income used for
    rate purpose only) to get Aggregate_Income.
    """
    # subtract TI_special_rates from TTI to get Aggregate_Income, which is
    # the portion of TTI that is taxed at normal rates
    taxinc = TTI - TI_special_rates
    taxinc = max(0., taxinc)
    agginc = taxinc + Income_Rate_Purpose
    agginc = max(0., agginc)
    # Check this later
    Aggregate_Income = taxinc
    # calculate tax on taxable income subject to taxation at normal rates
    # NOTE: Tax_ST_CG_APPRATE is not calculated here because its stacking
    #       and scope assumptions have not been specified.  If it is ever
    #       calculated here, be sure to add it to Total_Tax_STCG variable.
    surcharge_rate1 = surcharge_rate[0]
    surcharge_rate2 = surcharge_rate[1]
    surcharge_rate3 = surcharge_rate[2]
    surcharge_thd1 = surcharge_thd[0]
    surcharge_thd2 = surcharge_thd[1]
    # compute tax on income taxed at normal rates
    tbrk1 = tbrk1[AGEGRP]
    tbrk2 = tbrk2[AGEGRP]
    tbrk3 = tbrk3[AGEGRP]
    tax_normal_rates = (rate1 * min(agginc, tbrk1) +
                        rate2 * min(tbrk2 - tbrk1, max(0., agginc - tbrk1)) +
                        rate3 * min(tbrk3 - tbrk2, max(0., agginc - tbrk2)) +
                        rate4 * max(0., agginc - tbrk3))
    tax_Aggregate_Income = tax_normal_rates
    # compute tax_TTI
    tax_TTI = tax_normal_rates + tax_TI_special_rates
    # rebate on agricultural income
    # agri income is exempt but used for rate purpose
    agri_inc = Income_Rate_Purpose + tbrk1
    rebate_agri = (rate1 * min(agri_inc, tbrk1) +
                   rate2 * min(tbrk2 - tbrk1, max(0., agri_inc - tbrk1)) +
                   rate3 * min(tbrk3 - tbrk2, max(0., agri_inc - tbrk2)) +
                   rate4 * max(0., agri_inc - tbrk3))
    # Acricultural rebate only applicable if taxinc is greater than tbrk1
    if taxinc <= tbrk1:
        rebate_agri = 0.
    # Acricultural rebate cannot be more than the tax liability
    rebate_agri = min(tax_TTI, rebate_agri)
    # Update tax_TTI after allowing agricultural rebate
    tax_TTI -= rebate_agri
    # Compute rebate amount u/s 87A. Only applicablle if TTI > rebate_thd
    if TTI > rebate_thd:
        rebate = 0.
    else:
        rebate = min(rebate_rate * TTI, rebate_ceiling)
    # As rebate is a non-refundable credit it should capped to tax_TTI
    rebate = min(tax_TTI, rebate)
    tax = tax_TTI - rebate
    # compute surcharge amount
    if TTI < surcharge_thd1:
        surcharge = tax * surcharge_rate1
    else:
        if TTI >= surcharge_thd1 and TTI < surcharge_thd2:
            surcharge = tax * surcharge_rate2
        else:
            surcharge = tax * surcharge_rate3
    tax += surcharge
    # compute cess amount
    cess = tax * cess_rate
    # compute pitax amount
    pitax = tax + cess
    Total_Tax_Cap_Gains = Total_Tax_STCG + Total_Tax_LTCG
    return (Aggregate_Income, tax_Aggregate_Income, rebate_agri, tax_TTI,
            Total_Tax_Cap_Gains, rebate, surcharge, cess, pitax)
