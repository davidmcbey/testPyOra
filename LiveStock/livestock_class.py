#-------------------------------------------------------------------------------
# Name:        livestock_class.py
# Purpose:     Functions to create TODO
# Author:      Dave Mcbey
# Created:     22/03/2020
# Description:
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'livestock_class.py'
__version__ = '0.0.0'
__author__ = 's02dm4'

from pandas import DataFrame, read_excel
from openpyxl import load_workbook


class Livestock:
    """Information on different types of livestock"""

    def __init__(self, livestock_data, crop_prod_data):

        livestock_data = livestock_data
        crop_prod_data = crop_prod_data
        self.region = livestock_data[1]['region']
        self.system = livestock_data[1]['system']
        livestock_info = livestock_data[1]['lvstck_grp']

        for livestock in livestock_info:
            livestock_name = livestock['type']
            strat = livestock['statgey']
            number = livestock['number']
            manure = livestock['manure']
            meat = livestock['meat']
            milk = livestock['milk']
            n_excrete = livestock['n_excrete']
            feeds = livestock['feeds']
            print (f'There are {number} {livestock_name}')




    '''
    def get_monthly_harvest_change(self, orator_obj, harvest_land_use_merged):

        df = harvest_land_use_merged

        # This is a list of dictionaries. Each dictionary is 1 months production for each farm area
        dictionary = df.to_dict(orient='records')
        # Iterate through dictionary to aggregate all data per month. This involves matching crops, adding yield change from
        # that crop to total, then dicviding total by number of areas (total tallied in 'crop_x_count' var below
        total_crop_A_change = 0
        total_crop_B_change = 0
        total_crop_C_change = 0
        total_crop_D_change = 0
        total_crop_E_change = 0

        for dic in dictionary:
            crop_A_count = 0
            crop_B_count = 0
            crop_C_count = 0
            crop_D_count = 0
            crop_E_count = 0

            crop_A_name = dic['area_1_crop']
            total_crop_A_change = dic['area_1_yield_change']
            crop_A_count += 1
            dic.update({"Crop_A_name": crop_A_name})
            dic.update({"Crop_A_tot_yield_change_month": total_crop_A_change})

            if dic['area_2_crop'] == dic['area_1_crop']:
                total_crop_A_change = (dic['area_1_yield_change'] + dic['area_2_yield_change'])
                crop_A_count += 1
                dic.update({"Crop_A_tot_yield_change_month":total_crop_A_change})
            else:
                crop_B_name = dic['area_2_crop']
                total_crop_B_change = dic['area_2_yield_change']
                crop_B_count += 1
                dic.update({"Crop_B_name": crop_B_name})
                dic.update({"Crop_B_tot_yield_change_month":total_crop_B_change})

            if dic['area_3_crop'] == dic['area_1_crop']:
                total_crop_A_change = (total_crop_A_change + dic['area_3_yield_change'])
                crop_A_count += 1
                dic.update({"Crop_A_tot_yield_change_month":total_crop_A_change})
            elif dic['area_3_crop'] == dic['area_2_crop']:
                total_crop_B_change = (total_crop_B_change + dic['area_3_yield_change'])
                crop_B_count += 1
                dic.update({"Crop_B_tot_yield_change_month": total_crop_B_change})
            else:
                total_crop_C_change = dic['area_3_yield_change']
                crop_C_name = dic['area_3_crop']
                crop_C_count += 1
                dic.update({"Crop_C_name": crop_C_name})
                dic.update({"Crop_C_tot_yield_change_month":total_crop_C_change})

            if dic['area_4_crop'] == dic['area_1_crop']:
                total_crop_A_change = (total_crop_A_change + dic['area_4_yield_change'])
                crop_A_count += 1
                dic.update({"Crop_A_tot_yield_change_month":total_crop_A_change})
            elif dic['area_4_crop'] == dic['area_2_crop']:
                total_crop_B_change = (total_crop_B_change + dic['area_4_yield_change'])
                crop_B_count += 1
                dic.update({"Crop_B_tot_yield_change_month": total_crop_B_change})
            elif dic['area_4_crop'] == dic['area_3_crop']:
                total_crop_C_change = (total_crop_C_change + dic['area_4_yield_change'])
                crop_C_count += 1
                dic.update({"Crop_C_tot_yield_change_month": total_crop_C_change})
            else:
                crop_D_name = dic['area_4_crop']
                dic.update({"Crop_D_name": crop_D_name})
                total_crop_D_change = dic['area_4_yield_change']
                crop_D_count += 1
                dic.update({"Crop_D_tot_yield_change_month":total_crop_D_change})

            if dic['area_5_crop'] == dic['area_1_crop']:
                total_crop_A_change = (total_crop_A_change + dic['area_5_yield_change'])
                crop_A_count += 1
                dic.update({"Crop_A_tot_yield_change_month":total_crop_A_change})
            elif dic['area_5_crop'] == dic['area_2_crop']:
                total_crop_B_change = (total_crop_B_change + dic['area_5_yield_change'])
                crop_B_count += 1
                dic.update({"Crop_B_tot_yield_change_month": total_crop_B_change})
            elif dic['area_5_crop'] == dic['area_3_crop']:
                total_crop_C_change = (total_crop_C_change + dic['area_5_yield_change'])
                crop_C_count += 1
                dic.update({"Crop_C_tot_yield_change_month": total_crop_C_change})
            elif dic['area_5_crop'] == dic['area_4_crop']:
                total_crop_D_change = (total_crop_D_change + dic['area_5_yield_change'])
                crop_D_count += 1
                dic.update({"Crop_D_tot_yield_change_month": total_crop_D_change})
            else:
                crop_E_name = dic['area_5_crop']
                dic.update({"Crop_E_name": crop_E_name})
                total_crop_E_change = dic['area_5_yield_change']
                crop_E_count += 1
                dic.update({"Crop_E_tot_yield_change_month":total_crop_E_change})

            if crop_A_count != 0:
                crop_A_tot = (total_crop_A_change / crop_A_count)
                dic.update({"Crop_A_tot_yield_change_month": crop_A_tot})
            if crop_B_count != 0:
                crop_B_tot = (total_crop_B_change / crop_B_count)
                dic.update({"Crop_B_tot_yield_change_month": crop_B_tot})
            if crop_C_count != 0:
                crop_C_tot = (total_crop_C_change / crop_C_count)
                dic.update({"Crop_C_tot_yield_change_month": crop_C_tot})
            if crop_D_count != 0:
                crop_D_tot = (total_crop_D_change / crop_D_count)
                dic.update({"Crop_D_tot_yield_change_month": crop_D_tot})
            if crop_E_count != 0:
                crop_E_tot = (total_crop_E_change / crop_E_count)
                dic.update({"Crop_E_tot_yield_change_month": crop_E_tot})

        # Remove all data apart from totals for the month, then return this list of dictionaries. add number showing month
        month = 1
        for dic in dictionary:
            del dic['area_1_crop']
            del dic['area_1_yield_change']
            del dic['area_2_crop']
            del dic['area_2_yield_change']
            del dic['area_3_crop']
            del dic['area_3_yield_change']
            del dic['area_4_crop']
            del dic['area_4_yield_change']
            del dic['area_5_crop']
            del dic['area_5_yield_change']
            dic.update({'month' : month})
            month += 1

        return dictionary

livestock_list = []
import matplotlib.pyplot as plt
from merge_data import merge_harvest_land_use

class Charts(object):
    Create charts
    def __init__(self, orator_obj):

        self.title = 'Chart creation'

        Create graphs with all livestock shown on it


        # Milk and Eggs
        # =============
        plt.style.use('seaborn')
        fig, ax = plt.subplots()
        liv_manure_10_yr_monthly = {}
        for livestock in livestock_list:
            ax.plot(livestock.atyp_milk_prod, linewidth=3, label=livestock.neat_name)

        plt.title("All livestock atypical milks/egg production", fontsize=24)
        plt.xlabel('Months since typical', fontsize=16)
        plt.ylabel('Production (Kg per year', fontsize=16)
        plt.legend(loc="upper right")
        plt.tick_params(axis='both', which='major', labelsize=16)
        plt.savefig('Outputs/Livestock/Graphs/all_livestock_milk_eggs_atypical.png', bbox_inches='tight')

        # Meat
        # ====
        plt.style.use('seaborn')
        fig, ax = plt.subplots()
        liv_manure_10_yr_monthly = {}
        for livestock in livestock_list:
            ax.plot(livestock.atyp_meat_prod, linewidth=3, label=livestock.neat_name)

        plt.title("All livestock atypical meat production", fontsize=24)
        plt.xlabel('Months since typical', fontsize=16)
        plt.ylabel('Production (Kg per year', fontsize=16)
        plt.legend(loc="upper right")
        plt.tick_params(axis='both', which='major', labelsize=16)
        plt.savefig('Outputs/Livestock/Graphs/all_livestock_meat_atypical.png', bbox_inches='tight')

        # Manure
        # ======
        plt.style.use('seaborn')
        fig, ax = plt.subplots()
        liv_manure_10_yr_monthly = {}
        for livestock in livestock_list:
            ax.plot(livestock.atyp_man_prod, linewidth=3, label=livestock.neat_name)

        plt.title("All livestock atypical manure production", fontsize=24)
        plt.xlabel('Months since typical', fontsize=16)
        plt.ylabel('Production (Kg per year', fontsize=16)
        plt.legend(loc="upper right")
        plt.tick_params(axis='both', which='major', labelsize=16)
        plt.savefig('Outputs/Livestock/Graphs/all_livestock_manure_atypical.png', bbox_inches='tight')

        # Excreted N
        # ==========
        plt.style.use('seaborn')
        fig, ax = plt.subplots()
        liv_manure_10_yr_monthly = {}
        for livestock in livestock_list:
            ax.plot(livestock.atyp_N_excr, linewidth=3, label=livestock.neat_name)

        plt.title("All livestock atypical Nitrogen excretion", fontsize=24)
        plt.xlabel('Months since typical', fontsize=16)
        plt.ylabel('N Excretions (Kg per year', fontsize=16)
        plt.legend(loc="upper right")
        plt.tick_params(axis='both', which='major', labelsize=16)
        plt.savefig('Outputs/Livestock/Graphs/all_livestock_nitrogen_atypical.png', bbox_inches='tight')

        # Create graph with data for each anml and production type
        # ==========================================================
        for livestock in livestock_list:
            plt.style.use('seaborn')
            fig, ax = plt.subplots()
            ax.plot(livestock.atyp_milk_prod, linewidth=3)

            #Set chart title and label access
            ax.set_title(f"Milk/Egg Production: {livestock.name}", fontsize=24)
            ax.set_xlabel("Months since typical", fontsize=14)
            ax.set_ylabel("Production (Kg per year", fontsize=14)

            #Set size of tick labels
            ax.tick_params(axis='both', labelsize=14)

            # Save output
            plt.savefig(f'Outputs/Livestock/Graphs/{livestock.neat_name}_milk_egg_prod_atypical.png', bbox_inches='tight')

        for livestock in livestock_list:
            plt.style.use('seaborn')
            fig, ax = plt.subplots()
            ax.plot(livestock.atyp_meat_prod, linewidth=3)

            #Set chart title and label access
            ax.set_title(f"Meat Production: {livestock.name}", fontsize=24)
            ax.set_xlabel("Months since typical", fontsize=14)
            ax.set_ylabel("Production (Kg per year", fontsize=14)

            #Set size of tick labels
            ax.tick_params(axis='both', labelsize=14)

            # Save output
            plt.savefig(f'Outputs/Livestock/Graphs/{livestock.neat_name}_meat_atypical.png', bbox_inches='tight')

        for livestock in livestock_list:
            plt.style.use('seaborn')
            fig, ax = plt.subplots()
            ax.plot(livestock.atyp_man_prod, linewidth=3)

            #Set chart title and label access
            ax.set_title(f"Manure Production: {livestock.name}", fontsize=24)
            ax.set_xlabel("Months since typical", fontsize=14)
            ax.set_ylabel("Production (Kg per year", fontsize=14)

            #Set size of tick labels
            ax.tick_params(axis='both', labelsize=14)

            # Save output
            plt.savefig(f'Outputs/Livestock/Graphs/{livestock.neat_name}_man_prod_atypical.png', bbox_inches='tight')

        for livestock in livestock_list:
            plt.style.use('seaborn')
            fig, ax = plt.subplots()
            ax.plot(livestock.atyp_N_excr, linewidth=3)

            #Set chart title and label access
            ax.set_title(f"N Excretion: {livestock.name}", fontsize=24)
            ax.set_xlabel("Months since typical", fontsize=14)
            ax.set_ylabel("Excretion (Kg per year", fontsize=14)

            #Set size of tick labels
            ax.tick_params(axis='both', labelsize=14)

            # Save output
            plt.savefig(f'Outputs/Livestock/Graphs/{livestock.neat_name}_N_excretion_atypical.png', bbox_inches='tight')
            '''

