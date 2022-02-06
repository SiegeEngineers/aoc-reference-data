import logging
from ..commons.errors import (
    DoubletteFoundError,
    MissingKeyError,
)
from ..commons import INDEX_LIST_SUFFIX

LOGGER = logging.getLogger(__name__)


class Indexable(object):
    def __init__(self):
        pass

    def check_duplicates(index_list):

        # index_list:
        # Tuple(
        #     Player/Team/Platform ID,
        #     Index in parsed List,
        #     ItemID
        # )

        duplicates = []

        unpacked_root_ids = []
        unpacked_idz = []
        unpacked_item_ids = []

        # Unpack index lists
        for root_id, idx, item_id in index_list:

            if unpacked_item_ids.count(item_id) > 0:
                doublette_index = unpacked_item_ids.index(item_id)

                doublette_tuple = tuple(
                    (
                        (
                            unpacked_root_ids[doublette_index],
                            unpacked_idz[doublette_index],
                            unpacked_item_ids[doublette_index],
                        ),
                        (root_id, idx, item_id),
                    )
                )

                duplicates.append(doublette_tuple)
            else:
                unpacked_root_ids.append(root_id)
                unpacked_idz.append(idx)
                unpacked_item_ids.append(item_id)

        return duplicates

    def check_for_doublettes(self):
        """Checks for duplicates in the indexed keys.

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

        for key, unique, optional, sub_key_settings in self.index_key_settings:
            if not unique:
                break

            if sub_key_settings is None:
                attribute_name = self.get_attribute_name(key)
                index_list = getattr(self, attribute_name)

                errors.append(
                    self.duplicates_error_builder(
                        Indexable.check_duplicates(index_list), key, None
                    )
                )

            else:
                for (
                    sub_key,
                    unique,
                    optional,
                    third_lvl_key_settings,
                ) in sub_key_settings:
                    if not unique:
                        break
                    if third_lvl_key_settings is None:
                        attribute_name = self.get_attribute_name(key, sub_key)
                        index_list = getattr(self, attribute_name)

                        errors.append(
                            self.duplicates_error_builder(
                                Indexable.check_duplicates(index_list),
                                key,
                                sub_key,
                            )
                        )

        return errors

    def duplicates_error_builder(self, duplicates, key, sub_key):

        errors = []

        if len(duplicates) > 0:
            for offset, duplicate in enumerate(duplicates):

                unique_id_help_text = ""

                if key == "id":
                    unique_id_help_text = f"""

Help: If you need a unique id,
try to use the following 'id: {self.get_new_unique_id(offset=offset+1)}'
                        """

                errors.append(
                    DoubletteFoundError(
                        f"""
We found a duplicate!

Duplicated value is: {duplicate[0][2]}

We've found it in:
1. {type(self)}::ID({duplicate[0][0]})::'{key}'
2. {type(self)}::ID({duplicate[1][0]})::'{key}'
{unique_id_help_text}
"""
                    )
                )

        return errors

    def get_attribute_name(self, key, sub_key=None):
        """Compose an attribute name and return it as string

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
        """Composes the name of an attribute and creates it in 'self'

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

    def index_sub_key(
        self,
        attr,
        key,
        sub_key,
        sub_key_attribute_name=None,
        optional=True,
        sub_key_settings=None,
    ):
        """Indexes a sub-key of a given attribute (e.g. players, teams)

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
        err = self.index_key(
            attr=attr,
            key=key,
            sub_key=sub_key,
            sub_key_attribute_name=sub_key_attribute_name,
            optional=optional,
            sub_key_settings=sub_key_settings,
        )
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

    def index_key(
        self,
        attr,
        key,
        sub_key=None,
        sub_key_attribute_name=None,
        optional=True,
        sub_key_settings=None,
    ):
        """Indexes a key of a given attribute (e.g. players, teams)

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
            LOGGER.debug(f"Creating index for '{attr}[<element>].{key}'")
        elif sub_key_settings is not None:
            for sub_key, unique, sk_optional, sk_settings in sub_key_settings:

                LOGGER.debug(
                    f"Creating index for '{attr}<element>.{key}.{sub_key}]'"
                )
                attribute_name = self.create_attribute(key, sub_key)
                err = self.index_sub_key(
                    attr=attr,
                    key=key,
                    sub_key=sub_key,
                    sub_key_attribute_name=attribute_name,
                    optional=sk_optional,
                    sub_key_settings=sk_settings,
                )
                if err is not None:
                    errors.append(err)

            err_len = len(errors)

            if err_len == 0:
                LOGGER.debug(
                    f"No errors. Indexing '{type(self)}'::'{key}.{sub_key}' "
                    "finished."
                )
                return None
            elif err_len > 0:
                LOGGER.error(
                    f"Indexing '{type(self)}'::'{key}[{sub_key}]' "
                    f"finished with {err_len} error(s)."
                )
                return errors

        for index, elem in enumerate(getattr(self, attr)):
            if attr == "teams":

                # Minimal hack to check if the attribute exists
                # without implementing an iterator for Team
                if key in elem.__dict__:
                    if isinstance(getattr(elem, key), int):
                        # Create tuple(team_id, team_index, team_id)
                        # and add to index set
                        # For consistency
                        tpl = tuple(
                            (
                                getattr(elem, "id"),
                                index,
                                getattr(elem, key),
                            )
                        )

                        getattr(self, attribute_name).append(tpl)

                    elif isinstance(getattr(elem, key), str):
                        # Use lower-case for strings for easier
                        # comparison
                        # Create tuple(team_id, team_index, team_name)
                        # and add to index set
                        tpl = tuple(
                            (
                                getattr(elem, "id"),
                                index,
                                getattr(elem, key).lower(),
                            )
                        )

                        getattr(self, attribute_name).append(tpl)

                    elif isinstance(getattr(elem, key), (set, list)):
                        # Create tuple(team_id, team_index, player_id)
                        # and add to index set
                        for player_id in getattr(elem, key):
                            tpl = tuple(
                                (
                                    getattr(elem, "id"),
                                    index,
                                    player_id,
                                )
                            )

                            getattr(self, attribute_name).append(tpl)

                else:
                    errors.append(
                        MissingKeyError(
                            f"Missing '{type(self)}'::'{key}' "
                            f"for "
                            f"'{getattr(elem,key)}'"
                        )
                    )

            elif attr == "players":
                if sub_key is not None and key != "platforms":
                    if sub_key in getattr(elem, key).keys():
                        for sk_elem in getattr(elem, key).sub_key:
                            LOGGER.debug(
                                f"Found: {elem['id']} - "
                                f"{sub_key}::{sk_elem}"
                            )
                            # Create
                            # tuple(player_id, player_index, sk_elem)
                            # and add to index set
                            tpl = tuple(
                                (
                                    getattr(elem, "id"),
                                    index,
                                    sk_elem,
                                )
                            )

                            getattr(self, sub_key_attribute_name).append(tpl)

                elif key == "platforms":
                    platform_ids = getattr(
                        elem, key
                    ).get_platform_ids_for_platform(sub_key)

                    if platform_ids is not None:
                        for platform_id in platform_ids:
                            # Create
                            # tuple(player_id, player_index, sk_elem)
                            # and add to index set
                            tpl = tuple(
                                (
                                    getattr(elem, "id"),
                                    index,
                                    platform_id,
                                )
                            )

                            getattr(self, sub_key_attribute_name).append(tpl)

                elif (
                    sub_key is not None
                    and sub_key not in getattr(elem, key).__dict__
                ):
                    raise NotImplementedError()
                elif sub_key is None:
                    # Minimal hack to check if the attribute exists
                    # without implementing an iterator for Player
                    if key in elem.__dict__ and elem.__dict__[key] is not None:
                        # Create
                        # tuple(player_id, player_index, value of field)
                        # and add to index set
                        tpl = tuple(
                            (
                                getattr(elem, "id"),
                                index,
                                getattr(elem, key)
                                if not isinstance(getattr(elem, key), str)
                                else getattr(elem, key).lower(),
                            )
                        )
                        getattr(self, attribute_name).append(tpl)

                    elif key not in elem.__dict__ and optional:
                        pass
                    elif (
                        key in elem.__dict__
                        and optional
                        and elem.__dict__[key] is None
                    ):
                        pass
                    elif key not in elem.__dict__ and not optional:
                        errors.append(
                            MissingKeyError(
                                f"Missing non-optional {type(self)}::"
                                f"'name' {key} for '{elem}'"
                            )
                        )

        err_len = len(errors)

        if err_len > 0 and key == "id":
            new_id = self.get_new_unique_id(key)
            errors.append(
                f"Help: If you need a next unique ID "
                f"for {type(self)}::{key}' "
                f"start from 'id: {new_id}' onwards."
            )

        if err_len == 0:
            LOGGER.debug(
                f"No errors. Indexing '{type(self)}'::'{key}' finished."
            )
            return None
        elif err_len > 0:
            LOGGER.error(
                f"Indexing '{type(self)}'::'{key}' finished with "
                f"{err_len} error(s)."
            )
            return errors
