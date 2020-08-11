#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 21:14:03 2020

@author: RMS671214
"""


# %%
import QuantLib as ql
import pandas as pd

# As usual, let us start by importing the QuantLib library and pick a 
# valuation date and set the calculation instance evaluation date.
value_date = ql.Date(17, 6, 2021)
ql.Settings.instance().evaluationDate = value_date


# %%
# For simplicity, let us imagine that the treasury yield curve is flat.
# This makes it easier to construct the yield curve easily.
# This also allows us to directly shock the yield curve, and provides a
# validation for the more general treatment of shocks on yield curve.
ytm = ql.SimpleQuote(0.02)
rate_handle = ql.QuoteHandle(ytm)
day_count = ql.ActualActual(ql.ActualActual.ISMA)
calendar = ql.Singapore()
ts_yield = ql.FlatForward(value_date, rate_handle, day_count)
ts_handle = ql.YieldTermStructureHandle(ts_yield)


# %%
# Now let us construct the bond itself. We do that by first constructing the
# schedule, and then passing the schedule into the bond.
issue_date = ql.Date(17, 6, 2020)
maturity_date = ql.Date(17, 6, 2030)
tenor = ql.Period(ql.Semiannual)
calendar = ql.Singapore()
bussiness_convention = ql.Unadjusted
date_generation = ql.DateGeneration.Backward
month_end = False
schedule = ql.Schedule(issue_date, maturity_date, 
                        tenor, calendar, 
                        ql.Unadjusted,
                        ql.Unadjusted, 
                        date_generation, 
                        month_end)
bondSche = list(schedule)
print('+++++++++++++++++')
print('COUPON DATES')
print(bondSche)

print('=============')

# %%

settlement_days = 0
day_count = ql.ActualActual(ql.ActualActual.ISMA)
coupon_rate = 0.02
coupons = [coupon_rate]

# Now lets construct the FixedRateBond
settlement_days = 0
face_value = 100
fixed_rate_bond = ql.FixedRateBond(settlement_days,
                                   face_value,
                                   schedule,
                                   coupons,
                                   day_count)

# %%

bond_engine = ql.DiscountingBondEngine(ts_handle)
fixed_rate_bond.setPricingEngine(bond_engine)
npv = fixed_rate_bond.NPV()
print(npv)



#%%

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Create bond object using schedule
# FixedRateBond is an overloaded function.
# Please see the manual for other ways to create bond object
bond = ql.FixedRateBond( 0, 100.0, schedule,[0.02], ql.ActualActual(ql.ActualActual.ISMA))
rate = ql.InterestRate(0.02, ql.ActualActual(ql.ActualActual.ISMA), ql.Compounded, ql.Semiannual)
price = ql.BondFunctions.cleanPrice(bond, rate)
print(price)

# %%

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# This is how to collect information from QuantLib to get information
# on the coupon structure
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


cpn_structure = []
schelen = len(schedule)
for i in range(schelen - 1):
    ql.Settings.instance().evaluationDate = schedule[i]
    coupons = {}
    coupons['current_date'] = schedule[i].ISO()
    coupons['previous_coupon_rate'] = ql.BondFunctions.previousCouponRate(bond)
    coupons['next_coupon_rate'] = ql.BondFunctions.nextCouponRate(bond)
    coupons['accrual_start'] = ql.BondFunctions.accrualStartDate(bond).ISO()
    coupons['accrual_end'] = ql.BondFunctions.accrualEndDate(bond).ISO()
    coupons['accrual_period'] = ql.BondFunctions.accrualPeriod(bond)
    coupons['accrual_days'] = ql.BondFunctions.accrualDays(bond)
    coupons['accrued_period'] = ql.BondFunctions.accruedPeriod(bond)
    coupons['accrued_days'] = ql.BondFunctions.accruedDays(bond)
    coupons['accrued_amount'] = ql.BondFunctions.accruedAmount(bond)
    coupons['coupon_interest'] = ql.FixedRateCoupon(
        ql.BondFunctions.accrualEndDate(bond), 100_000_000,
        coupons['next_coupon_rate'],
        ql.ActualActual(ql.ActualActual.ISMA),
        ql.BondFunctions.accrualStartDate(bond),
        ql.BondFunctions.accrualEndDate(bond)).amount()
    #print(schedule[i], coupons['accrual_start'], coupons['accrual_end'])
    cpn_structure.append(coupons)
    

#print(cpn_structure[2]['coupon_interest'].amount())

ql.Settings.instance().evaluationDate = value_date
sche = pd.DataFrame(cpn_structure)
#print(sche)


# %%




# %%
