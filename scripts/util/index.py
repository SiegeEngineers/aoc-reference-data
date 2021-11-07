import logging
from .error import DoubletteFoundError, MissingKeyError
from . import INDEX_LIST_SUFFIX

LOGGER = logging.getLogger(__name__)


class Indexable(object):
    def __init__(self):
        pass

    # def next_free_id(self, jump_index=None, recursion=False, ci=False):
    #     LOGGER.info("Getting next free id ...")
    #     self.index_id_list(jump_index, recursion, ci)
    #     return max(self.id_list) + 1

    def get_new_unique_id(self, key, sub_key=None, ci=False):
        LOGGER.debug("Getting new unique id ...")
        attribute_name = self.get_attribute_name(key, sub_key)
        return max(getattr(self, attribute_name)) + 1

    def check_for_doublettes(self, key, sub_key_settings=None, optional=True, ci=False):
        errors = []

        if sub_key_settings is not None:
            for sub_key, unique, sk_optional, sk_settings in sub_key_settings:
                LOGGER.debug(f"Checking for doublettes in '{key}[{sub_key}]' ...")
                attribute_name = self.get_attribute_name(key, sub_key)
                (duplicate, duplicate_idx) = Indexable.list_has_duplicate(
                    getattr(self, attribute_name))

                if duplicate:
                    LOGGER.debug(f"ERROR! '{type(self)}::{key}[{sub_key}]' "
                                 f"list contains a duplicate!")
                    errors.append(DoubletteFoundError(f"""'{type(self)}::'{key}[{sub_key}]': """
                                                      f"""{getattr(self, attribute_name)[duplicate_idx]}"""
                                                      ))
            else:
                LOGGER.debug(f"No duplicates in '{type(self)}::{key}[{sub_key}]' found.")

        elif sub_key_settings is None:
            attribute_name = self.get_attribute_name(key)
            LOGGER.debug(f"Checking for doublettes in '{key}' ...")
            (duplicate, duplicate_idx) = Indexable.list_has_duplicate(
                getattr(self, attribute_name))

            if duplicate:
                LOGGER.debug(f"ERROR! '{type(self)}::{key}' "
                             f"list contains a duplicate!")
                errors.append(DoubletteFoundError(f"""'{type(self)}::'{key}': """
                                                  f"""{getattr(self, attribute_name)[duplicate_idx]}"""
                                                  ))
            else:
                LOGGER.debug(f"No duplicates in '{type(self)}::{key}' found.")

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug(f"No errors. Checking for duplicates in '{type(self)}::'{key}' finished.")
            return None
        if err_len > 0:
            LOGGER.error(f"Checking for duplicates in '{type(self)}::'{key}' finished with {err_len} error(s).")
            return errors

    def list_has_duplicate(lst):
        for index, elem in enumerate(lst):
            if lst.count(elem) > 1:
                return (True, index)
        return (False, -1)

    def get_attribute_name(self, key, sub_key=None):
        if sub_key is None:
            attribute_name = f"{key}_{INDEX_LIST_SUFFIX}"
        elif sub_key is not None:
            attribute_name = f"{key}_{sub_key}_{INDEX_LIST_SUFFIX}"
        return attribute_name

    def create_attribute(self, key, sub_key=None):
        if sub_key is None:
            attribute_name = f"{key}_{INDEX_LIST_SUFFIX}"
        elif sub_key is not None:
            attribute_name = f"{key}_{sub_key}_{INDEX_LIST_SUFFIX}"

        setattr(self, attribute_name, [])
        return attribute_name

    def index_sub_key(self, attr, key, sub_key, sub_key_attribute_name=None,
                      optional=True, sub_key_settings=None, ci=False):
        errors = []
        err = self.index_key(attr=attr, key=key, sub_key=sub_key,
                             sub_key_attribute_name=sub_key_attribute_name,
                             optional=optional, sub_key_settings=sub_key_settings)
        if err is not None:
            errors.append(err)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug(f"No errors. Indexing '{type(self)}::'{key}[{sub_key}]' finished.")
            return None
        if err_len > 0:
            LOGGER.error(f"Indexing '{type(self)}::'{key}[{sub_key}]' finished with {err_len} error(s).")
            return errors

    def index_key(self, attr, key, sub_key=None, sub_key_attribute_name=None,
                  optional=True, sub_key_settings=None, ci=False):

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
                LOGGER.debug(f"Creating index for '{attr}['element'][{key}][{sub_key}]'")
                attribute_name = self.create_attribute(key, sub_key)
                err = self.index_sub_key(attr=attr, key=key, sub_key=sub_key,
                                         sub_key_attribute_name=attribute_name,
                                         optional=sk_optional,
                                         sub_key_settings=sk_settings)
                if err is not None:
                    errors.append(err)

            err_len = len(errors)

            if err_len == 0:
                LOGGER.debug(f"No errors. Indexing '{type(self)}'::'{key}[{sub_key}]' finished.")
                return None
            if err_len > 0:
                LOGGER.error(f"Indexing '{type(self)}'::'{key}[{sub_key}]' finished with {err_len} error(s).")
                return errors

        for index, elem in enumerate(getattr(self, attr)):
            if attr == "teams":
                try:
                    if getattr(elem, key) is not None:
                        getattr(self, attribute_name).append(
                            getattr(elem, key))
                    else:
                        errors.append(MissingKeyError(f"Missing '{key}' "
                                                      f"for "
                                                      f"'{getattr(elem,'name')}'"))

                except (KeyError, AttributeError):
                    try:
                        errors.append(MissingKeyError(f"Missing '{key}' "
                                                      f"for '{getattr(elem, 'name')}'"))
                    except AttributeError:
                        errors.append(MissingKeyError(f"Missing non-optional 'name' key "
                                                      f"for '{elem}'"))
            elif attr == "players":
                if sub_key is not None:
                    try:
                        for sk_elem in elem[key][sub_key]:
                            LOGGER.debug(f"Found: {elem['id']} - {sub_key}::{sk_elem}")
                            getattr(self, sub_key_attribute_name).append(sk_elem)
                    except KeyError:
                        if not optional:
                            errors.append(MissingKeyError(f"Missing '{key}::{sub_key}' "
                                                          f"for '{elem['id']}:{elem['name']}'"))
                elif sub_key is None:
                    # As long as we don't parse as a class, this should work.
                    # Otherwise the key is None and existing, see teams above
                    try:
                        getattr(self, attribute_name).append(elem[key])
                    except KeyError:
                        if not optional:
                            try:
                                errors.append(MissingKeyError(f"Missing '{key}' "
                                                              f"for '{elem['name']}'"))
                            except KeyError:
                                errors.append(MissingKeyError(f"Missing non-optional 'name' key "
                                                              f"for '{elem}'"))

        err_len = len(errors)

        if err_len > 0 and key == 'id':
            new_id = self.get_new_unique_id(key)
            errors.append(f"Help: If you need a next unique ID for {type(self)}'::'{key}' "
                          f"try adding 'id: {new_id}'")

        if err_len == 0:
            LOGGER.debug(f"No errors. Indexing '{type(self)}'::'{key}' finished.")
            return None
        if err_len > 0:
            LOGGER.error(f"Indexing '{type(self)}'::'{key}' finished with {err_len} error(s).")
            return errors
