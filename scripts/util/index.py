import logging
from .error import DoubletteFoundError, MissingKeyError
from . import INDEX_LIST_SUFFIX

LOGGER = logging.getLogger(__name__)


class Indexable(object):
    def __init__(self):
        pass

    def get_new_unique_id(self, key, sub_key=None, offset=1):
        """ Returns a unique ID for 'self'.'key'.

        Args:
            key (str): Key part of key:value.
            sub_key (str, optional): Next level in hierarchy of 'key'.
                                        Defaults to None.

        Returns:
            int: a unique ID derived from the maximum ID of a the
                 index element list with the addition of 1
        """

        LOGGER.debug("Getting new unique id ...")
        attribute_name = self.get_attribute_name(key, sub_key)
        return max(getattr(self, attribute_name)) + offset

    def check_for_doublettes(self, key, sub_key_settings=None, optional=True):
        """ Checks for duplicates in the indexed keys.

        Args:
            key (str): Key part of key:value.
            sub_key (str, optional): Next level in hierarchy of 'key'.
                                        Defaults to None.
            optional (bool, optional): Defines whether the key in the element
                                       is optional. Defaults to True.

        Returns:
            DoubletteFoundError: Returns 'DoubletteFoundError(s)' appended to
                                 a list of Errors
        """

        errors = []
        dupl = []

        if sub_key_settings is not None:
            for sub_key, unique, sk_optional, sk_settings in sub_key_settings:
                LOGGER.debug(f"Checking for doublettes in '{key}[{sub_key}]' "
                             "...")

                attribute_name = self.get_attribute_name(key, sub_key)

                (duplicate, duplicate_idx) = Indexable.list_has_duplicate(
                    getattr(self, attribute_name))

                if not duplicate:
                    LOGGER.debug(f"No duplicates in '{type(self)}::{key}' "
                                 "found.")

                while duplicate:
                    LOGGER.debug(f"ERROR! '{type(self)}::{key}[{sub_key}]' "
                                 f"list contains a duplicate!")

                    # Collect duplicates
                    dupl.append(getattr(self, attribute_name)[duplicate_idx])

                    # Check if there are more duplicates after this duplicate
                    (duplicate, duplicate_idx) = Indexable.list_has_duplicate(
                        getattr(self, attribute_name),
                        dupl=dupl,
                        start=duplicate_idx
                    )

                merged_duplicates = {dup for dup in dupl}

                offset = 1
                for duplicate in merged_duplicates:
                    if key == 'id':
                        errors.append(
                            DoubletteFoundError(
                                f"We found a duplicate: '{type(self)}::'{key}'"
                                f": {duplicate}. "
                                f"Help: If you need a unique id, try 'id: "
                                f"""{self.get_new_unique_id(
                                    key=key, offset=offset
                                )}'"""
                            ))
                        offset += 1
                    else:
                        errors.append(DoubletteFoundError(
                            f"We found a duplicate: '{type(self)}::"
                            f"'{key}[{sub_key}]': {duplicate}"
                        ))

        elif sub_key_settings is None:
            attribute_name = self.get_attribute_name(key)

            LOGGER.debug(f"Checking for doublettes in '{key}' ...")

            (duplicate, duplicate_idx) = Indexable.list_has_duplicate(
                getattr(self, attribute_name))

            if not duplicate:
                LOGGER.debug(f"No duplicates in '{type(self)}::{key}' found.")

            while duplicate:
                LOGGER.debug(f"ERROR! '{type(self)}::{key}' "
                             f"list contains a duplicate!")

                # Collect duplicates
                dupl.append(getattr(self, attribute_name)[duplicate_idx])

                # Check if there are more duplicates after this duplicate
                (duplicate, duplicate_idx) = Indexable.list_has_duplicate(
                    getattr(self, attribute_name),
                    dupl=dupl,
                    start=duplicate_idx
                )

            merged_duplicates = {dup for dup in dupl}

            offset = 1
            for duplicate in merged_duplicates:
                if key == 'id':
                    errors.append(DoubletteFoundError(
                        f"We found a duplicate: '{type(self)}::'{key}': "
                        f"{duplicate}. "
                        f"Help: If you need a unique id, try 'id: "
                        f"{self.get_new_unique_id(key, offset=offset)}'"
                    ))
                    offset += 1
                else:
                    errors.append(DoubletteFoundError(
                        f"We found a duplicate: '{type(self)}::'{key}': "
                        f"{duplicate}"
                    ))

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug(f"No errors. Checking for duplicates in "
                         f"'{type(self)}::'{key}' finished.")
            return None
        elif err_len > 0:
            LOGGER.error(f"Checking for duplicates in '{type(self)}::'{key}' "
                         f"finished with {err_len} error(s).")
            return errors

    def list_has_duplicate(lst, dupl=None, start=None):
        """ Checks the input list for a duplicate number

        Args:
            lst(list): A list to be checked for a duplicate
            dupl(list): A list of already detected duplicates in that 'key'
            start(int, optional): The index from where to start. Defaults to
            None.

        Returns:
            (bool, int): Returns a tuple of True and the index of the duplicate
                         ID in case a duplicate was found. If no duplicate was
                         found it returns a tuple of False and None.
        """

        for index, elem in enumerate(lst):
            if start is not None and index <= start:
                continue
            elif lst.count(elem) > 1:
                if ((dupl is not None) and (elem not in dupl)) or dupl is None:
                    return (True, index)

        return (False, None)

    def get_attribute_name(self, key, sub_key=None):
        """ Compose an attribute name and return it as string

        Args:
            key (str): Key part of key:value.
            sub_key (String, optional): Next level in hierarchy of 'key'.
                                        Defaults to None.

        Returns:
            str: Returns the assembled attribute name
        """

        if sub_key is None:
            attribute_name = f"{key}_{INDEX_LIST_SUFFIX}"
        elif sub_key is not None:
            attribute_name = f"{key}_{sub_key}_{INDEX_LIST_SUFFIX}"
        return attribute_name

    def create_attribute(self, key, sub_key=None):
        """ Composes the name of an attribute and creates it in 'self'

        Args:
            key (str): Key part of key:value.
            sub_key (String, optional): Next level in hierarchy of 'key'.
                                        Defaults to None.

        Returns:
            str: Returns the assembled attribute name
        """

        if sub_key is None:
            attribute_name = f"{key}_{INDEX_LIST_SUFFIX}"
        elif sub_key is not None:
            attribute_name = f"{key}_{sub_key}_{INDEX_LIST_SUFFIX}"

        setattr(self, attribute_name, [])
        return attribute_name

    def index_sub_key(self, attr, key, sub_key, sub_key_attribute_name=None,
                      optional=True, sub_key_settings=None):
        """ Indexes a sub-key of a given attribute (e.g. players, teams)

        Args:
            attr (str): E.g. player, team (identical with the parsed lists from
                        the repository)
            key (str): Key part of key:value.
            sub_key (str, optional): Next level in hierarchy of 'key'.
                                        Defaults to None.
            sub_key_attribute_name (str, optional): Needed to create its own
                                                    index list.
                                                    Defaults to None.
            optional (bool, optional): Mostly needed to check if we should
                                       throw errors for non-existent 'keys'.
                                       Defaults to True, meaning we should
                                       explicitly state whether something
                                       is non-optional.
            sub_key_settings (tuple(IndexSetting), optional): IndexSetting
                                                              tuple to be
                                                              used in
                                                              recursive mode.
                                                              Defaults to None.

        Returns:
            list: Returns a list of errors that this method throws.
        """
        errors = []
        err = self.index_key(attr=attr, key=key, sub_key=sub_key,
                             sub_key_attribute_name=sub_key_attribute_name,
                             optional=optional,
                             sub_key_settings=sub_key_settings)
        if err is not None:
            errors.append(err)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug(
                f"No errors. Indexing '{type(self)}::'{key}[{sub_key}]' "
                "finished."
            )
            return None
        elif err_len > 0:
            LOGGER.error(
                f"Indexing '{type(self)}::'{key}[{sub_key}]' finished with "
                f"{err_len} error(s)."
            )
            return errors

    def index_key(self, attr, key, sub_key=None, sub_key_attribute_name=None,
                  optional=True, sub_key_settings=None):
        """ Indexes a key of a given attribute (e.g. players, teams)

        Args:
            attr (str): E.g. player, team (identical with the parsed lists from
                        the repository)
            key (str): Key part of key:value.
            sub_key (str, optional): Next level in hierarchy of 'key'.
                                        Defaults to None.
            sub_key_attribute_name (str, optional): Needed to create its own
                                                    index list.
                                                    Defaults to None.
            optional (bool, optional): Mostly needed to check if we should
                                       throw errors for non-existent 'keys'.
                                       Defaults to True, meaning we should
                                       explicitly state whether something
                                       is non-optional.
            sub_key_settings (tuple(IndexSetting), optional): IndexSetting
                                                              tuple to be
                                                              used in
                                                              recursive mode.
                                                              Defaults to None.

        Returns:
            list: Returns a list of errors that this method throws.
        """

        errors = []

        if sub_key is None and sub_key_settings is None:
            attribute_name = self.create_attribute(key)
            LOGGER.debug(f"Creating index for '{attr}['element'][{key}][]'")
        elif sub_key is not None and sub_key_settings is None:
            # Last sub_key in hierarchy
            pass
        elif sub_key_settings is not None:
            for sub_key, unique, sk_optional, sk_settings in sub_key_settings:
                pass
                LOGGER.debug(
                    f"Creating index for '{attr}['element'][{key}][{sub_key}]'"
                )
                attribute_name = self.create_attribute(key, sub_key)
                err = self.index_sub_key(attr=attr, key=key, sub_key=sub_key,
                                         sub_key_attribute_name=attribute_name,
                                         optional=sk_optional,
                                         sub_key_settings=sk_settings)
                if err is not None:
                    errors.append(err)

            err_len = len(errors)

            if err_len == 0:
                LOGGER.debug(
                    f"No errors. Indexing '{type(self)}'::'{key}[{sub_key}]' "
                    "finished."
                )
                return None
            elif err_len > 0:
                LOGGER.error(f"Indexing '{type(self)}'::'{key}[{sub_key}]' "
                             f"finished with {err_len} error(s).")
                return errors

        for index, elem in enumerate(getattr(self, attr)):
            if attr == "teams":
                try:
                    if getattr(elem, key) is not None:
                        getattr(self, attribute_name).append(
                            getattr(elem, key))
                    else:
                        errors.append(MissingKeyError(
                            f"Missing '{type(self)}'::'{key}' "
                            f"for "
                            f"'{getattr(elem,'name')}'"))

                except (KeyError, AttributeError):
                    try:
                        errors.append(MissingKeyError(
                            f"Missing '{type(self)}::{key}' "
                            f"for '{getattr(elem, 'name')}'"))
                    except AttributeError:
                        errors.append(MissingKeyError(
                            f"Missing non-optional 'name' key "
                            f"for '{elem}'"))
            elif attr == "players":
                if sub_key is not None:
                    try:
                        for sk_elem in elem[key][sub_key]:
                            LOGGER.debug(f"Found: {elem['id']} - "
                                         f"{sub_key}::{sk_elem}")
                            getattr(self,
                                    sub_key_attribute_name
                                    ).append(sk_elem)
                    except KeyError:
                        if not optional:
                            errors.append(MissingKeyError(
                                f"Missing '{type(self)}::{key}::{sub_key}' "
                                f"for '{elem['id']}:{elem['name']}'"))
                elif sub_key is None:
                    # As long as we don't parse as a class, this should work.
                    # Otherwise the key is None and existing, see teams above
                    try:
                        getattr(self, attribute_name).append(elem[key])
                    except KeyError:
                        if not optional:
                            try:
                                errors.append(
                                    MissingKeyError(f"Missing {type(self)}:"
                                                    f":{key}' "
                                                    f"for '{elem['name']}'"))
                            except KeyError:
                                errors.append(
                                    MissingKeyError(
                                        f"Missing non-optional {type(self)}::"
                                        f"'name' key for '{elem}'"))

        err_len = len(errors)

        if err_len > 0 and key == 'id':
            new_id = self.get_new_unique_id(key)
            errors.append(f"Help: If you need a next unique ID "
                          f"for {type(self)}::{key}' "
                          f"start from 'id: {new_id}' onwards.")

        if err_len == 0:
            LOGGER.debug(
                f"No errors. Indexing '{type(self)}'::'{key}' finished.")
            return None
        elif err_len > 0:
            LOGGER.error(f"Indexing '{type(self)}'::'{key}' finished with "
                         f"{err_len} error(s).")
            return errors
