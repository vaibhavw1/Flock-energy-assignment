def decode_sveltekit_data(values, index):
    """
    Decode indexed references in the observed
    SvelteKit serialized data format.
    """

    if not isinstance(index, int) or isinstance(index, bool):
        raise ValueError("Invalid SvelteKit reference")

    if index < 0 or index >= len(values):
        raise ValueError("SvelteKit reference out of range")

    value = values[index]

    if isinstance(value, dict):
        return {
            key: decode_sveltekit_data(values, ref)
            for key, ref in value.items()
        }

    if isinstance(value, list):
        return [
            decode_sveltekit_data(values, ref)
            for ref in value
        ]

    return value


def normalize_meter_details(response):
    """
    Extract meter details and hierarchy from
    the observed SvelteKit response.
    """

    nodes = response["nodes"]

    meter_node = nodes[2]

    values = meter_node["data"]

    decoded = decode_sveltekit_data(values, 0)

    details = decoded["detail"]["data"]

    meter_info = {
        item["parameterName"]: item["parameterValue"]
        for item in details
    }

    return {
        "meterId": decoded["meterId"],
        "details": meter_info,
        "hierarchy": decoded["hierarchy"]
    }