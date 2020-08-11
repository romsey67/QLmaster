#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 16:49:59 2020

@author: RMS671214
"""

import QuantLib as ql
import pandas as pd

# %%
# The Rates
st_curve = {'1W': 2.00, '1M': 2.10, '3M': 2.20, '6M': 2.30}



# %%

# some constants and conventions
# here we just assume for the sake of example
# that some of the constants are the same for 
# st rates and lt rates

value_date = ql.Date(17, 6, 2020)
ql.Settings.instance().evaluationDate = value_date

calendar = ql.Singapore()
bussiness_convention = ql.Unadjusted
day_count = ql.ActualActual
end_of_month = True
settlement_days = 0
face_amount = 100
coupon_frequency = ql.Period(ql.Semiannual)
settlement_days = 0


# %%

# create deposit rate helpers from depo_rates
depo_helpers = [ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(st_curve[key]/100.0)),
                                     ql.Period(key),
                                     0,
                                     ql.Singapore(),
                                     ql.ModifiedFollowing,
                                     True,
                                     ql.Actual365Fixed())
                for key in st_curve]
# print(list(depo_helpers))

# %%
ql_stcurve = ql.PiecewiseLogCubicDiscount(value_date, depo_helpers,
                                       ql.Actual365Fixed())

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# This is the only way to retrieve the discount factors with QuantLib
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
df = list(map(lambda x: {"date": x.ISO(), 'df': ql_stcurve.discount(x)},
              ql_stcurve.dates()))
df2 = list(map(lambda x: {"date": x.ISO(), 'df': ql_stcurve.discount(x)},
              ql_stcurve.dates()))
print('====DF1====')
print(df)
print('====DF2====')
print(df2)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Calculation of fraction of a year with QuantLib
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
yearfrac = [ql.Actual365Fixed().yearFraction(value_date, adate) for
            adate in ql_stcurve.dates()]
print(yearfrac)
dflist = [datum['df'] for datum in df]
print(dflist)

itime = ql.Actual365Fixed().yearFraction(value_date, ql.Date(25,11,2020))
print(itime)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Interpolation with QuantLib
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
ipolate = ql.LogCubicNaturalSpline(yearfrac, dflist)
irate = ipolate(0.0821917808219178, allowExtrapolation=False)

print('irate==>',irate)


# %%
# create fixed rate bond helpers from fixed rate bonds
lt_curve = {'1Y': 2.40, '2Y': 2.50, '3Y': 2.60, '5Y': 2.70, '7Y': 2.80,
            '10Y': 2.90, '30Y': 3.00}
lt_helpers = []

for key in lt_curve:
    termination_date = value_date + ql.Period(key)
   
    schedule = ql.Schedule(value_date,
                           termination_date,
                           ql.Period(ql.Semiannual),
                           ql.Singapore(),
                           ql.ModifiedFollowing,
                           ql.ModifiedFollowing,
                           ql.DateGeneration.Backward,
                           True)

    lt_helper = ql.FixedRateBondHelper(ql.QuoteHandle(ql.SimpleQuote(100)),
                                        0,
                                        100,
                                        schedule,
                                        [lt_curve[key]/100.0],
                                        ql.Actual365Fixed(),
                                        ql.Following,
                                        )
    lt_helpers.append(lt_helper)


# %%
# The yield curve is constructed here
rate_helpers = depo_helpers + lt_helpers
yieldcurve = ql.PiecewiseLogCubicDiscount(value_date,
                             rate_helpers,
                             ql.Actual365Fixed())

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# This is the only way to retrieve the discount factors with QuantLib
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
newdf = list(map(lambda x: {"date": x, 'df': yieldcurve.discount(x)},
              yieldcurve.dates()))
print(newdf)

# %%

# get spot rates
rate_info = []

for d in yieldcurve.dates():
    datum = {}
    datum['date'] = d.ISO()
    datum['df'] = yieldcurve.discount(d)
    yrs = ql.Actual365Fixed().yearFraction(value_date, d)
    datum['time'] = yrs
    compounding = ql.Compounded
    freq = ql.Semiannual
    zero_rate = yieldcurve.zeroRate(yrs, compounding, freq)
    eq_rate = zero_rate.equivalentRate(ql.Actual365Fixed(),
                                       compounding,
                                       freq,
                                       value_date, d).rate()
    cont_rate = zero_rate.equivalentRate(ql.Actual365Fixed(),
                                       ql.Continuous,
                                       freq,
                                       value_date, d).rate()
    datum['spot'] = eq_rate * 100
    datum['continuous'] = cont_rate * 100
    rate_info.append(datum)

print(rate_info)
pdrate = pd.DataFrame(rate_info)
# %%

