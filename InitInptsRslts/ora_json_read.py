#-------------------------------------------------------------------------------
# Name:        ora_json_read.py
# Purpose:     a collection of reusable functions
# Author:      Mike Martin
# Created:     26/10/2020
# Licence:     <your licence>
# Definitions:
#   spin_up
#
# Description:
#
#
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'ora_json_read.py'
__version__ = '0.0.0'

# Version history
# ---------------
#
import json
from glob import glob
from os.path import isfile, normpath, join

from ora_excel_read import check_integrity_run_xlxs_file

ERROR_STR = '*** Error *** '
METRIC_LIST = list(['precip', 'tair'])
FNAME_RUN = 'FarmWthrMgmt.xlsx'
JSON_TYPES = {'lvstck': 'livestock'}
CLIMATE_TYPES = {'A':'Arid/semi-arid', 'H': 'humid/sub-humid', 'T':'Tropical highlands or temperate'}
FARMING_TYPES = {'LG':'Livestock grazing', 'MR':'Mixed rotation'}
STRATEGIES = list(['On farm production', 'Buy/sell'])

'''
=========== Livestock ==============
'''
def _region_validate(site_defn, anml_prodn_obj):
    '''
    TODO: improve - issue error
    '''
    region = site_defn['region']
    if region not in anml_prodn_obj.africa_regions:
        region = anml_prodn_obj.africa_regions[-1]

    return region

def _farming_system(site_defn):
    '''
    should be 3 characters, capitals
    '''
    system = site_defn['system'].upper()
    if len(system) < 3:
        system = 'MRA'  # TODO: issue warning

    else:
        farming_type = system[0:2]
        if farming_type not in FARMING_TYPES:
            farming_type = 'MR'  # TODO: issue warning

        climate_type = system[2]
        if climate_type not in CLIMATE_TYPES:
            climate_type = 'A'

        system = farming_type + climate_type

    return system

class LivestockEntity:

    def __init__(self, lvstck_content, anml_prodn_obj):
        '''
        TODO: improve
        '''
        type = lvstck_content['type']
        if type not in anml_prodn_obj.africa_anml_types:
            type = anml_prodn_obj.africa_anml_types[-1]

        number = float(lvstck_content['number'])    # TODO: trap error
        strategy = lvstck_content['strategy']
        if strategy not in STRATEGIES:
            strategy = STRATEGIES[-1]

        feeds = []
        for key in lvstck_content:
            if key.find('feed') > -1:
                feed_type = lvstck_content[key]['type']
                if feed_type ==  'bought in':
                    value = lvstck_content[key]['value']
                else:
                    if feed_type not in anml_prodn_obj.crop_names:
                        feed_type = anml_prodn_obj.crop_names[-1]

                    try:
                        value = lvstck_content[key]['value']
                    except KeyError as err:
                        value = None

                feeds.append({'type':feed_type, 'value': value})

        self.type = type
        self.number = number
        self.statgey = strategy
        self.feeds = feeds
        self.manure = None
        self.n_excrete = None
        self.meat = None
        self.milk = None

class ReadLvstckJsonSubareas(object, ):

    def __init__(self, lvstck_files, anml_prodn_obj):
        '''
        read and validate livestock JSON file
        '''
        print('Reading livestock JSON files...')

        subareas = {}

        for lvstck_fname in lvstck_files:

            # avoid error when user has removed a management file during a session
            # ====================================================================
            if not isfile(lvstck_fname):
                continue

            with open(lvstck_fname, 'r') as flvstck:
                lvstck_content = json.load(flvstck)

            site_defn = lvstck_content['site definition']
            area = site_defn['area name']
            region = _region_validate(site_defn, anml_prodn_obj)
            system = _farming_system(site_defn)

            lvstck_grp = []
            for key in site_defn:
                if key.find('livestock') > -1:
                    lvstck_grp.append(LivestockEntity(site_defn[key], anml_prodn_obj))

            subareas[area] = {'region': region, 'system': system, 'lvstck_grp': lvstck_grp}

        self.subareas = subareas
        print()     # cosmetic

def check_json_xlsx_inp_files(w_soil_cn, settings, mgmt_dir):
    '''
    =========== called during initialisation or from GUI ==============
    validate management files
    two types of JSON files - either: 'mgmt' for crop management or: 'lvstck' for livestock
    '''
    nfiles = {}
    mess = 'JSON files:  '
    for jtype in JSON_TYPES:
        json_type = JSON_TYPES[jtype]

        ok_json_files = []
        json_files = glob(mgmt_dir + '/*' + jtype + '.json')
        if len(json_files) > 0:
            for json_fname in json_files:
                json_fname = normpath(json_fname)
                try:
                    with open(json_fname, 'r') as fmgmt:
                        mgmt_content = json.load(fmgmt)
                        # TODO: to log file?                print('Read management input file ' + json_fname)
                        ok_json_files.append(json_fname)

                except (json.JSONDecodeError, OSError, IOError) as err:
                    print(str(err))
                    print('Could not read ' + json_type + ' input file ' + json_fname)


        settings[jtype + '_files'] = ok_json_files

        # build message
        # =============
        nfiles[jtype] = len(ok_json_files)
        mess += '{} {}  '.format(nfiles[jtype], json_type)

    # activate carbon nitrogen model push button
    # ==========================================
    w_soil_cn.setEnabled(False)
    farm_wthr_fname = FNAME_RUN
    mess += '\t\trun file, ' + farm_wthr_fname + ', is '

    wthr_xls = join(mgmt_dir, farm_wthr_fname)
    if (isfile(wthr_xls)):
        ret_var = check_integrity_run_xlxs_file(wthr_xls)
        if ret_var is None:
            mess += 'uncompliant'
        else:
            subareas = ret_var[0]
            if len(subareas) == 0:
                mess += 'present but with no subareas'
            else:
                w_soil_cn.setEnabled(True)
                mess += 'present with subareas: '
                for sba in subareas:
                    mess += sba + ', '
                mess = mess.rstrip(', ')
    else:
        mess += 'does not exist'

    return mess

def disp_ow_parms(form):
    '''
    display summary of selected organic waste type
    '''
    ow_parms = form.ora_parms.ow_parms

    # build message
    # =============
    ow_type = form.w_combo13.currentText()
    pcnt_c = round(ow_parms[ow_type]['pcnt_c']*100, 3)
    pcnt_urea = round(ow_parms[ow_type]['pcnt_urea']*100, 3)
    ann_c_input = round(ow_parms[ow_type]['ann_c_input']*100, 3)

    mess = 'Organic waste parameters:\t% Carbon: {}\t'.format(pcnt_c)
    mess += '\t%C wrt untreated waste: {}\t\t% Ammonia or urea-N in manure: {}'.format(ann_c_input, pcnt_urea)

    return mess

def check_mngmnt_ow(form):
    '''
    display summary of selected organic waste type
    '''

    # TODO - delete if unnecessary

    '''
    # check first 12 months
    # =====================
    if hasattr(form, 'ora_subareas'):
        subareas = form.ora_subareas
        for sba in subareas:
            for imnth in range(12):
    '''

    # build message
    # =============
    ow_type = form.w_combo13.currentText()
    mnth_appl = form.w_mnth_appl.currentText()

    mess = 'Extra {} will be applied in {}'.format(ow_type, mnth_appl)

    return mess