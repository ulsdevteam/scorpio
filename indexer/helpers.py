import shortuuid


def generate_identifier():
    # TODO: do we need to check uniqueness?
    return shortuuid.uuid()
