def dotted_startswith(src, dst):
    """
    Decide if the first argument starts with the second argument
    considering both use dot notation like in logging.

    Return true if all of the parts of the second argument are present
    in the first argument.
    """
    src_chunks = src.split('.')
    dst_chunks = dst.split('.')
    if len(dst) > len(src):
        # If dst is more specific than src is not compatible with dst
        return False
    # The dst is either less or equaly specific than src. Compare if all
    # common chunks are the same.
    return all([x == y for x, y in zip(dst, src)])
