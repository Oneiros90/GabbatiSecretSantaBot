import datetime
from functools import wraps
from typing import Optional, Union

from telegram import User

import utilities
from config import config

NAME_MAX_LENGTH = 100


def update_time(func):
    @wraps(func)
    def wrapped(instance, *args, **kwargs):
        result = func(*args, **kwargs)
        instance.updated()
        return result

    return wrapped


class SecretSanta:
    def __init__(
            self,
            origin_message_id: int,
            user_id: int,
            user_name: str,
            chat_id: int,
            chat_title: str,
            santa_message_id: Optional[int] = None,
            participants: Optional[dict] = None,
            created_on: Optional[datetime.datetime] = None,
            updated_on: Optional[datetime.datetime] = None,
            started: bool = False,
            started_on: Optional[datetime.datetime] = None,
    ):
        now = utilities.now()
        self._santa_dict = {
            "origin_message_id": origin_message_id,  # message received from the user in the group
            "santa_message_id": santa_message_id,  # message we send in the group
            "participants": participants or {},
            "created_on": created_on or now,
            "updated_on": updated_on or now,
            "user_id": user_id,
            "user_name": user_name,
            "chat_id": chat_id,
            "chat_title": chat_title,
            "started": started,
            "started_on": started_on,
        }

    @classmethod
    def from_dict(cls, santa_dict: dict):
        return cls(
            origin_message_id=santa_dict["origin_message_id"],
            user_id=santa_dict["user_id"],
            user_name=santa_dict["user_name"],
            chat_id=santa_dict["chat_id"],
            chat_title=santa_dict["chat_title"],
            santa_message_id=santa_dict["santa_message_id"],
            participants=santa_dict["participants"],
            created_on=santa_dict["created_on"],
            updated_on=santa_dict["updated_on"],
            started=santa_dict["started"],
            started_on=santa_dict.get("started_on", None),
        )

    def dict(self):
        return self._santa_dict

    @property
    def creator_id(self):
        return self._santa_dict["user_id"]

    @property
    def creator_name(self):
        return self._santa_dict["user_name"]

    @property
    def creator_name_escaped(self):
        return utilities.html_escape(self.creator_name)

    @property
    def chat_id(self):
        return self._santa_dict["chat_id"]

    @property
    def chat_title(self):
        return self._santa_dict["chat_title"]

    @property
    def chat_title_escaped(self):
        return utilities.html_escape(self.chat_title)

    @property
    def origin_message_id(self):
        return self._santa_dict["origin_message_id"]

    @property
    def santa_message_id(self):
        return self._santa_dict["santa_message_id"]

    @santa_message_id.setter
    def santa_message_id(self, santa_message_id):
        self._santa_dict["santa_message_id"] = santa_message_id

    @property
    def started(self):
        return self._santa_dict["started"]

    @started.setter
    def started(self, new_value):
        self._santa_dict["started"] = new_value

    @property
    def started_on(self):
        return self._santa_dict["started_on"]

    @started_on.setter
    def started_on(self, new_value):
        self._santa_dict["started_on"] = new_value

    @property
    def message_id(self):
        return self.santa_message_id

    @property
    def id(self):
        return self.santa_message_id

    @property
    def participants(self) -> dict:
        return self._santa_dict["participants"]

    @property
    def updated_on(self):
        return self._santa_dict["updated_on"]

    @staticmethod
    def user_id(user_id: Union[int, User]):
        if isinstance(user_id, User):
            return user_id.id

        return user_id

    @property
    def created_on(self):
        return self._santa_dict["created_on"]

    def get_participants_count(self):
        return len(self.participants)

    def get_missing_count(self):
        return config.santa.min_participants - self.get_participants_count()

    # @update_time
    def add(
            self,
            user: User,
            match_message_id: Optional[int] = None,
            join_message_id: Optional[int] = None,
    ) -> bool:
        already_a_participant = user.id in self.participants

        self._santa_dict["participants"][user.id] = {
            "name": user.first_name[:NAME_MAX_LENGTH],
            "match_message_id": match_message_id,
            "last_join_message_id": join_message_id
        }

        return already_a_participant

    # @update_time
    def update_user_name(self, user: Union[User, str]):
        name = user
        if isinstance(user, User):
            name = user.first_name

        self._santa_dict["participants"][user.id]["name"] = name[:NAME_MAX_LENGTH]

    def is_duplicate_name(self, name):
        name_lower = name.lower()[:NAME_MAX_LENGTH]
        for user_id, user_data in self.participants.items():
            if user_data["name"].lower() == name_lower:
                return name[:NAME_MAX_LENGTH]  # we return the saved name (that is, shortened), for clarity

        return False

    # @update_time
    def remove(self, user: Union[int, User]) -> bool:
        user_id = self.user_id(user)
        result = bool(self._santa_dict["participants"].pop(user_id, None))
        return result

    def updated(self):
        self._santa_dict["updated_on"] = utilities.now()

    def start(self):
        self.started = True
        self.started_on = utilities.now()

    def is_participant(self, user: Union[int, User]) -> bool:
        user_id = self.user_id(user)
        return user_id in self.participants

    def is_creator(self, user: Union[int, User]) -> bool:
        user_id = self.user_id(user)
        return self.creator_id == user_id

    def get_user_match_message_id(self, user: Union[int, User]) -> int:
        user_id = self.user_id(user)
        # noinspection PyTypeChecker
        return self._santa_dict["participants"][user_id]["match_message_id"]

    def set_user_match_message_id(self, user: Union[int, User], message_id: int):
        user_id = self.user_id(user)
        self._santa_dict["participants"][user_id]["match_message_id"] = message_id

    def get_user_join_message_id(self, user: Union[int, User]) -> int:
        user_id = self.user_id(user)
        # noinspection PyTypeChecker
        return self._santa_dict["participants"][user_id]["last_join_message_id"]

    def set_user_join_message_id(self, user: Union[int, User], message_id: int):
        user_id = self.user_id(user)
        self._santa_dict["participants"][user_id]["last_join_message_id"] = message_id

    def get_user_name(self, user: Union[int, User]) -> str:
        user_id = self.user_id(user)
        # noinspection PyTypeChecker
        return self._santa_dict["participants"][user_id]["name"]

    def set_user_name(self, user: Union[int, User], name: str):
        user_id = self.user_id(user)
        self._santa_dict["participants"][user_id]["name"] = name

    def user_mention_escaped(self, user: Union[int, User]) -> str:
        user_id = self.user_id(user)
        # noinspection PyTypeChecker
        name = self._santa_dict["participants"][user_id]["name"]

        return utilities.mention_escaped_by_id(user_id, name)

    def link(self):
        link = ""
        if utilities.is_supergroup(self.chat_id):
            link = utilities.message_link(self.chat_id, self.santa_message_id, force_private=True)

        return link

    def inline_link(self, text: str, escape=False):
        if not utilities.is_supergroup(self.chat_id):
            return text

        link = self.link()
        text = text if not escape else utilities.html_escape(text)
        return f"<a href=\"{link}\">{text}</a>"

    def __str__(self):
        return f"{type(self).__name__}(id={self.origin_message_id}, participants={self.get_participants_count()}, updated_on={self.updated_on})"

