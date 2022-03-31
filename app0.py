"""
app0.py illustrates use of pitaxcalc-demo release 2.0.0 (India version).
USAGE: python app0.py > app0.res
CHECK: Use your favorite Windows diff utility to confirm that app0.res is
       the same as the app0.out file that is in the repository.
"""
from taxcalc import *

# create Records object containing pit.csv and pit_weights.csv input data
recs = Records()

assert isinstance(recs, Records)
assert recs.data_year == 2017
assert recs.current_year == 2017

# create GSTRecords object containing gst.csv and gst_weights.csv input data
grecs = GSTRecords()

assert isinstance(grecs, GSTRecords)
assert grecs.data_year == 2017
assert grecs.current_year == 2017

# create CorpRecords object containing cit.csv and cit_weights.csv input data
crecs = CorpRecords()

assert isinstance(crecs, CorpRecords)
assert crecs.data_year == 2017
assert crecs.current_year == 2017

policy_filename = "current_law_policy_new.json"
# create Policy object containing current-law policy
pol = Policy(DEFAULTS_FILENAME=policy_filename)
#pol = Policy()

assert isinstance(pol, Policy)
assert pol.current_year == 2017

# specify Calculator object for current-law policy
#calc1 = Calculator(policy=pol, records=recs, gstrecords=grecs,
#                   corprecords=crecs, verbose=False)

calc1 = Calculator(policy=pol, corprecords=crecs, verbose=False)

# NOTE: calc1 now contains a PRIVATE COPY of pol and a PRIVATE COPY of recs,
#       so we can continue to use pol and recs in this script without any
#       concern about side effects from Calculator method calls on calc1.

assert isinstance(calc1, Calculator)
assert calc1.current_year == 2017

calc1.calc_all()

start_year = 2017
end_year = 2023
wt_cit = []
i=0
for year in range(start_year, end_year):
       calc1.advance_to_year(year)    
       calc1.calc_all()
       weighted_citax1 = calc1.weighted_total_cit('citax')
       weighted_citax1_bn = round(weighted_citax1/10**7, 2)
       wt_cit += [weighted_citax1_bn]
print(wt_cit)
dump_vars = calc1.read_calc_variables()
# dump_vars = ['ID_NO', 'citax']
dumpdf = calc1.dataframe_cit(dump_vars)
column_order = dumpdf.columns

assert len(dumpdf.index) == calc1.carray_len

#dumpdf.to_csv('taxcalc/testdump.csv', index=False)
