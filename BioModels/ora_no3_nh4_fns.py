#-------------------------------------------------------------------------------
# Name:        ora_no3_nh4_fns.py
# Purpose:     a collection of reusable functions
# Author:      Mike Martin
# Created:     26/12/2019
# Licence:     <your licence>
#
# Description:
#    From 2.4. Soil nitrogen
#    Based on content in "Report on modelling work done for BREAD 101218v2_print.pdf"
#    Nitrogen is assumed to be held in 6 pools in the soil:
#            mineral N (nitrate and ammonium) and organic N (DPM, RPM, BIO and HUM-N)
#    loss by each process is adjusted using a loss adjustment ratio to account for
#    the losses by the other processes so that all processes are assumed to occur simultaneously
#    there is a critical minimum level of minimum N, below which, the mineral N cannot fall
#    The nitrate and ammonium pools are initialised at the minimum level, and the model run for 10 years
#    to establish the amount of nitrate or ammonium at the start of the forward run.
#    NO2 = nitrite; NO3 = nitrate; NH4 = ammonium; N2O = nitrous oxide; NO = nitric oxide
#
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'ora_no3_nh4_fns.py'
__version__ = '0.0.0'

# Version history
# ---------------
#
from math import exp
from calendar import monthrange

N_DENITR_DAY_MAX = 0.2      # Maximum potential denitrification rate in 1 cm layer, used in function  no3_denitrific

def prop_n_opt_from_soil_n_supply(soil_n_sply, nut_n_fert , nut_n_min, nut_n_opt):
    '''

    '''
    prop_n_opt = (soil_n_sply + nut_n_fert - nut_n_min)/(nut_n_opt - nut_n_min)  # (eq.3.3.1)

    return max( min(prop_n_opt,1), 0)

def prop_n_optimal_from_yield(prop_yld_opt, crop_vars):
    '''
    calculate proportion of the optimum supply of N in the soil using fitted curve coefficients
    pXopt = a pYldopt3 + b pYldopt2 + c pYldopt + d
    '''
    prop_n_opt = crop_vars['n_rcoef_a'] * prop_yld_opt**3 + crop_vars['n_rcoef_b'] * prop_yld_opt**2 + \
                                                    crop_vars['n_rcoef_c'] * prop_yld_opt + crop_vars['n_rcoef_d']
    return prop_n_opt


def get_n_parameters(n_parms):
    '''
    assume atmospheric deposition is composed of equal proportions of nitrate and ammonium-N
    This assumption may differ according to region
    '''
    atmos_n_depos = n_parms['atmos_n_depos']
    prop_atmos_dep_no3 = n_parms['prop_atmos_dep_no3']  # typically 0.5

    no3_atmos = prop_atmos_dep_no3 * atmos_n_depos/12  # atmospheric deposition of N to the soil (eq.2.4.2)
    nh4_atmos = (1 - prop_atmos_dep_no3) * atmos_n_depos/12  # (eq.2.4.19)
    k_nitrif = n_parms['k_nitrif']
    min_no3_nh4 = n_parms['no3_min']
    n_d50 = n_parms['n_d50']
    c_n_rat_som = n_parms['c_n_rat_som']
    precip_critic = n_parms['precip_critic']
    prop_volat = n_parms['prop_volat']
    
    return no3_atmos, nh4_atmos, k_nitrif, min_no3_nh4, n_d50, c_n_rat_som, precip_critic, prop_volat

def _fertiliser_inputs(fert_amount):
    '''
    Urea fertiliser (the main form of fertiliser used in Africa and India, decomposes on application
    to the soil to produce ammonium, therefore, the proportion of nitrate added in the fertiliser is zero (eq.2.3.5)
    '''
    prop_no3_to_fert = 0
    fert_to_no3_pool = prop_no3_to_fert * fert_amount

    return fert_to_no3_pool

'''
     =====================================
                Losses of nitrate
     =====================================
'''

def loss_adjustment_ratio(n_start, n_sum_inputs, n_sum_losses):
    '''
    for nitrate and ammonium (eq.2.4.1)
    unless losses are big or start plus inputs are small then value will be 1
    '''
    if n_sum_losses <= n_start + n_sum_inputs:
        loss_adj_rat = 1
    else:
        loss_adj_rat = (n_start + n_sum_inputs) / n_sum_losses

    return loss_adj_rat

def no3_immobilisation(soil_n_sply, nh4_immob, min_no3_nh4):
    '''
    A negative soil N supply represents immobilised N. Immobilisation is assumed to occur first from the ammonium pool.
    '''
    no3_immob = min( - min(soil_n_sply - nh4_immob, 0), min_no3_nh4) #  (eq.2.4.5)

    return no3_immob

def no3_leaching(precip, wc_start, pet, wc_fld_cap, no3_start, no3_inputs, no3_min):
    '''
    Nitrate-N lost by leaching is calculated from the concentration of available nitrate in the soil at the start of
    the time step plus any inputs of nitrate after dilution with rainwater and the water drained from the soil
        precip_t1       rainfall during the time step (mm)
        water_start     amount of water (mm) in the soil at the start of the time step
        water_t0        the soil water at time t0 (mm)
        pet_t1          potential evapotranspiration during the time step (mm)
        wc_fld_cap      field capacity (mm)
    no3_start, no3_inputs, no3_min
    '''

    # volume of water drained (mm) during the time step
    # =================================================
    wat_drain = max((precip - pet) - (wc_fld_cap - wc_start), 0)  # (eq.2.4.7)

    no3_leach = ((no3_start + no3_inputs - no3_min)/(wc_start + precip - pet))*wat_drain  # (eq.2.4.6)

    return  no3_leach, wat_drain

def no3_denitrific(imnth, t_depth, wat_soil, wc_pwp, wc_fld_cap, co2_aerobic_decomp, no3_avail, n_d50):
    '''
    Denitrification is a microbially facilitated process where nitrate is reduced and ultimately produces molecular
    nitrogen through a series of intermediate gaseous nitrogen oxide products. The process is performed primarily by
    heterotrophic bacteria although autotrophic denitrifiers have also been identified
    based on the simple approach used in ECOSSE
    '''
    no3_d50 = n_d50 * t_depth     # soil nitrate-N content at which denitrification is 50% of its full potential (kg ha-1)
    dummy, days_in_mnth = monthrange(2011, imnth)   # TODO: ignores leap year, is this correct?
    n_denit_max = min(no3_avail, N_DENITR_DAY_MAX * t_depth * days_in_mnth)    # (eq.2.4.9) maximum potential rate of denitrification (kg ha-1 month-1)

    rate_denit_no3 = no3_avail/(no3_d50 + no3_avail)    # (eq.2.4.10) nitrate rate modifier

    sigma_c = wat_soil   - wc_pwp       # calculated water content
    sigma_f = wc_fld_cap - wc_pwp       # field capacity maximum water content of the soil

    # Proportion of N2 produced by denitrification according to soil water and soil nitrate-N
    # =======================================================================================
    prop_n2_wat = 0.5*(sigma_c/sigma_f)                   # (eq.2.4.14)
    prop_n2_no3 = 1 - no3_avail/(40*t_depth + no3_avail)  # (eq.2.4.15)

    rate_denit_moist =  ((abs((sigma_c/sigma_f) - 0.62))/0.38)**1.74     # Grundmann and Rolston (1987)
    rate_denit_moist = min(1, rate_denit_moist)                     # (eq.2.4.11)

    # use the amount of CO2 produced by aerobic decomposition as a surrogate for biological activity
    # ==============================================================================================
    rate_denit_bio =  min(1, co2_aerobic_decomp * 0.1)    # (eq.2.4.12)

    n_denit = n_denit_max * rate_denit_no3 * rate_denit_moist * rate_denit_bio   # (eq.2.4.8)

    return n_denit, n_denit_max, rate_denit_no3, rate_denit_moist, rate_denit_bio, prop_n2_wat, prop_n2_no3

def no3_nh4_crop_uptake(prop_n_opt, n_respns_coef, nut_n_opt, t_grow, no3_avail, nh4_avail, pi_tonnes):
    '''
    crop N demand is calculated from proportion of optimum yield estimated assuming no other losses of mineral N
        0 <= prop_n_opt <= 1
        nut_n_opt:  N supply required for the optimum yield
        t_grow:     number of months in the growing season
        pi_tonnes:  used as a proxy to indicate if time step is in a growing season
    '''
    if pi_tonnes == 0:
        n_crop_dem, no3_crop_dem, n_crop_dem_adj, nh4_crop_dem, prop_yld_opt = 5*[0]
    else:
        # prop. of the optimum yield achieved for given prop. of the optimum supply of N, prop_n_opt
        # ==========================================================================================
        cn = n_respns_coef      # N response coefficient
        prop_yld_opt = (1 + cn)*prop_n_opt**cn - cn*(prop_n_opt)**(1 + cn) # (eq.2.4.16) and (eq.3.3.2)
        prop_yld_opt = max(min(prop_yld_opt, 1), 0.1)                      # see section 3.3

        n_crop_dem = nut_n_opt/t_grow    # N demand in each month without other losses
        n_crop_dem_adj = prop_n_opt * n_crop_dem  # (eq.2.4.17) N demand adjusted for other losses
        no3_crop_dem = n_crop_dem*(no3_avail/(no3_avail + nh4_avail))  # (eq.2.4.18) crop N demand from the nitrate pool

        '''
        as for nitrate, it is assumed that the crop N demand from the ammonium pool is shared equally between
        available nitrate and ammonium
        n_crop_dem: N demand of the crop in each month
        '''
        nh4_crop_dem = n_crop_dem * (nh4_avail / (no3_avail + nh4_avail))  # (eq.2.4.26)

    return n_crop_dem, n_crop_dem_adj, no3_crop_dem, nh4_crop_dem, prop_yld_opt

'''
     =====================================
                Ammonium functions
     =====================================
'''

def _nh4_atmos_deposition(n_atmos_depos, proportion = 0.5):
    '''
    atmospheric deposition of N to the soil (24)
    assume atmospheric deposition is composed of equal proportions of nitrate and ammonium-N
    This assumption may differ according to region.
    '''
    n_to_soil = n_atmos_depos*proportion

    return n_to_soil

def nh4_mineralisation(soil_n_sply):
    '''
    Mineralisation - Mineralisation of organic N is assumed to release N in the form of ammonium.
    Therefore, a positive net soil N supply, Nsoil (kg ha-1) (see section 3.3), is equivalent to the input
    of ammonium-N due to mineralisation, nh4,miner (kg ha-1),
    '''
    nh4_miner = max(soil_n_sply, 0)  # eq.2.4.21

    return nh4_miner

'''
     =====================================
                Losses of ammonium
     =====================================
'''
def nh4_immobilisation(soil_n_sply, nh4_min):
    '''
    Immobilisation – A negative soil N supply represents immobilised N and is assumed
    to occur first from the ammonium pool before drawing on nitrate.
    soil_n_sply:  soil N supply
    nh4_min:        minimum possible amount of ammonium-N,
    '''
    nh4_immob = min( - min(soil_n_sply, 0), nh4_min)    # (eq.2.4.22)

    return nh4_immob

def nh4_nitrification(nh4, nh4_min, rate_mod, k_nitrif):
    '''
    nitrified ammonium is assumed to occur by a first order reaction, using the same environmental
    rate modifiers as in soil organic matter decomposition
    k_nitrif - rate constant for nitrification, per month
    '''
    rate_inhibit = 1     # inhibition rate modifier TODO - see manual

    tmp_var = nh4 * (1 - exp(-k_nitrif*rate_mod*rate_inhibit))

    nh4_nitrif = min(tmp_var, nh4 - nh4_min)  # (eq.2.4.23)

    return nh4_nitrif

def nh4_volatilisation(precip, nh4_ow_fert, nh4_inorg_fert, precip_critic, prop_volat):
    '''
    Ammonia volatilisation: a chemical process that occurs at the soil surface when ammonium from urea or
    ammonium-containing fertilisers (e.g. urea) is converted to ammonia gas at high pH. Losses are minimal when
    fertiliser is incorporated, but can be high when fertiliser is surface-applied.

    a fixed proportion of the ammonium-N or urea-N in applied manure and fertilisers is assumed to be lost in the
    month of application only if the rainfall in that month is less than a critical level (< 21 mm)
    uses:
     prop_volat:        proportion of ammonium-N or urea-N that can be volatilised
     precip_critic:     critical level of rainfall below which losses due to volatilisation take place
    '''
    if precip < precip_critic:
        nh4_volat = prop_volat*(nh4_ow_fert + nh4_inorg_fert)   # (eq.2.4.25)
    else:
        nh4_volat = 0.0

    return  nh4_volat

