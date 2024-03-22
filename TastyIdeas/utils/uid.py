from uuid import UUID


def is_valid_uuid(uuid_to_test: str, version: int = 4) -> bool:
    """
This function checks whether the provided string, `uuid_to_test`, conforms to the format of a valid UUID
(Universally Unique Identifier).

 Parameters
 ----------
 uuid_to_test : str
     The string to be tested for validity as a UUID.
 version : {1, 2, 3, 4}
     Optional parameter specifying the UUID version. By default, it's set to 4.

 Returns
 -------
 bool
     Returns `True` if the input string is a valid UUID, otherwise returns `False`.
    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test