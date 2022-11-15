"""
app_dist_Tables00.py illustrates use of pitaxcalc-demo release 2.0.0
(India version).
USAGE: python app_dist_Tables00.py
"""
import locale
from taxcalc import *
from ind_curr import curr_ind

# locale.setlocale(locale.LC_ALL, '')
n = 123456789
print("INR {}".format(curr_ind(n)))

recs = Records(data='pit.csv', weights='pit_weights.csv')
grecs = GSTRecords()
crecs = CorpRecords()

# create Policy object containing current-law policy
pol = Policy()

# # specify Calculator object for current-law policy
# calc1 = Calculator(policy=pol, records=recs, gstrecords=grecs, corprecords=crecs, verbose=False)

# # specify Calculator object for reform in JSON file
# reform = Calculator.read_json_param_objects('Budget2019_reform.json', None)
# pol.implement_reform(reform['policy'])
# calc2 = Calculator(policy=pol, records=recs, gstrecords=grecs, corprecords=crecs, verbose=False)

# calc1.calc_all()
# calc2.calc_all()
# output_in_averages = False
# output_categories = 'standard_income_bins'
# dt1, dt2 = calc1.distribution_tables(calc2, output_categories,
#                                      averages=output_in_averages,
#                                      scaling=True)

# pd.options.display.float_format = '{:,.3f}'.format



# create Records object containing pit.csv and pit_weights.csv input data
recs = Records(data='pit.csv', weights='pit_weights.csv')
crecs = CorpRecords()

# create Policy object containing current-law policy
pol = Policy()

# specify Calculator object for current-law policy
calc1 = Calculator(policy=pol, records=recs, gstrecords=grecs, corprecords=crecs, verbose=False)

# specify Calculator object for reform in JSON file
reform = Calculator.read_json_param_objects('Budget2019_reform.json', None)
pol.implement_reform(reform['policy'])
calc2 = Calculator(policy=pol, records=recs, gstrecords=grecs, corprecords=crecs, verbose=False)
# loop through years 2017, 2018, and 2019 and print out pitax
for year in range(2017, 2020):
    calc1.advance_to_year(year)
    calc2.advance_to_year(year)
    calc1.calc_all()
    calc2.calc_all()
    weighted_tax1 = calc1.weighted_total('pitax')
    weighted_tax2 = calc2.weighted_total('pitax')
    total_weights = calc1.total_weight()
    print(f'****************  Total Tax Collection for {year}', end=' ')
    print('****************')
    print('\n')
    print(f'Current Law: Tax Collection in Cr. for {year}:', end=' ')
    print(f'{weighted_tax1 * 1e-7:,.2f} Cr.')
    print(f'Reform     : Tax Collection in Cr. for {year}:', end=' ')
    print(f'{weighted_tax2 * 1e-7:,.2f} Cr.')
    print('               Difference in Tax Collection:', end=' ')
    print(f'{(weighted_tax2-weighted_tax1) * 1e-7:,.2f} Cr.')
    print('\n')
    print(f'Representing: {total_weights * 1e-5:,.2f} Lakh taxpayers')
    print('\n')
    output_in_averages = False
    output_categories = 'standard_income_bins'
    # pd.options.display.float_format = '{:,.3f}'.format
    # dt1, dt2 = calc1.distribution_tables(calc2, 'weighted_deciles')
    dt1, dt2 = calc1.distribution_tables(calc2, output_categories,
                                         averages=output_in_averages,
                                         scaling=True)
    dt2['pitax diff'] = dt2['pitax'] - dt1['pitax']
    if (output_categories == 'standard_income_bins'):
        dt1.rename_axis('Income Bracket', inplace=True)
        dt2.rename_axis('Income Bracket', inplace=True)
    else:
        dt1.rename_axis('Decile', inplace=True)
        dt2.rename_axis('Decile', inplace=True)
    dt1 = dt1.reset_index().copy()
    dt2 = dt2.reset_index().copy()
    dt1 = dt1.fillna(0)
    dt2 = dt2.fillna(0)
    if output_in_averages:
        print('***************************  Average Tax Burden ', end=' ')
        print(f'(in Rs.) per Taxpayer for {year}  ***************************')
        pd.options.display.float_format = '{:,.0f}'.format
    else:
        print('*****************  Distribution Tables ', end=' ')
        print(f'for Total Tax Collection (in Rs. crores) for {year} *********')
        pd.options.display.float_format = '{:,.3f}'.format
    print('\n')
    print('     Current-Law Distribution Table')
    print('\n')
    print(dt1)
    print('\n')
    print('     Policy-Reform Distribution Table')
    print('\n')
    print(dt2)
    print('\n')
    # print text version of each complete distribution table to a file
    with open('dist-table-all-clp.txt', 'w') as dfile:
        dt1.to_string(dfile)
    with open('dist-table-all-ref.txt', 'w') as dfile:
        dt2.to_string(dfile)
    # print text version of each partial distribution table to a file
    to_include = ['weight', 'GTI', 'TTI', 'pitax']
    with open('dist-table-part-clp.txt', 'w') as dfile:
        dt1.to_string(dfile, columns=to_include)
    with open('dist-table-part-ref.txt', 'w') as dfile:
        dt2.to_string(dfile, columns=to_include)

