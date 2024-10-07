

def get_status_string(status_id):
    status_mapping = {
        '0': "Booked",
        '1': "Completed",
        '2': "Cancelled",
        '3': "Failed"
    }

    return status_mapping.get(status_id, "Unknown Status")