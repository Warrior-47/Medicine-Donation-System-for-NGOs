from itertools import groupby
from operator import itemgetter
from collections import namedtuple

def medicine_prioritized_data(donor_med_list, ngo_med_lists):
    result = { k: [data_to_list(v) for v in vs] for k, vs in groupby(ngo_med_lists, itemgetter('NGO'))}
    return med_priority_search(donor_med_list, result)


def med_priority_search(donor_med_list, ngo_med_lists):
    ngo_list = []
    ngo_details = namedtuple('NGODetails', 'pk fullname email phone')
    
    for ngo_id, info in ngo_med_lists.items():
        tot_priority = 0
        for med_info in info:
            for donor_med in donor_med_list:
                if donor_med.MedicineName == med_info.MedicineName:
                    tot_priority += med_info.MedicinePriority
        
        if tot_priority != 0:
            _, _, fullname, email, phone = info[0]
            store = ngo_details(ngo_id, fullname, email, phone)
            ngo_list.append((tot_priority, store))
        
        if len(ngo_list) == 5:
            break
    
    ngo_list = [ data for _, data in sorted(ngo_list, reverse=True) ]
    
    return ngo_list


def data_to_list(data: dict):
    data.pop('NGO')
    ordered_ngo_list = namedtuple('orderedNGOList', 'MedicineName MedicinePriority fullname email phone')
    res = ordered_ngo_list(data['MedicineName'], data['MedicinePriority'], data['NGO__fullname'], data['NGO__email'], data['NGO__phone'])
    return res