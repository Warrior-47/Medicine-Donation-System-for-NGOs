def medicine_prioritized_data(donor_med_list, ngo_med_lists, fetch_users):
    """Rank NGOs by how well their needs match the donor's medicines.

    donor_med_list: [{'MedicineName': ...}, ...] from medicine-service.
    ngo_med_lists:  [{'NGO_id': ..., 'MedicineName': ..., 'MedicinePriority': ...}, ...]
                    ordered by NGO_id, so each NGO's entries are contiguous.
    fetch_users:    callable(ids) -> [{'id': ..., 'fullname': ..., 'email': ...,
                    'phone': ...}, ...] resolving NGO details from user-service.

    Returns up to five NGOs as dicts with pk/fullname/email/phone keys,
    sorted by total matched priority, highest first (same semantics as the
    former monolith implementation, including the cap of five NGOs).
    """
    donor_names = {med['MedicineName'] for med in donor_med_list}

    totals = {}
    for med in ngo_med_lists:
        if med['MedicineName'] not in donor_names:
            continue
        ngo_id = med['NGO_id']
        if ngo_id not in totals and len(totals) == 5:
            # Entries are grouped by NGO_id, so a sixth matching NGO means
            # every remaining entry belongs to NGOs beyond the cap.
            break
        totals[ngo_id] = totals.get(ngo_id, 0) + med['MedicinePriority']

    if not totals:
        return []

    users = {user['id']: user for user in fetch_users(list(totals))}

    ranked = sorted(totals.items(), key=lambda item: (item[1], item[0]), reverse=True)
    return [
        {
            'pk': ngo_id,
            'fullname': users[ngo_id]['fullname'],
            'email': users[ngo_id]['email'],
            'phone': users[ngo_id]['phone'],
        }
        for ngo_id, _priority in ranked
        if ngo_id in users
    ]
