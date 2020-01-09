import shortuuid


def generate_identifier():
    # TODO: do we need to check uniqueness?
    shortuuid.set_alphabet('23456789abcdefghijkmnopqrstuvwxyz')
    return shortuuid.uuid()
