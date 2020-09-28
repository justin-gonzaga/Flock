import time
from database import database
from auth import auth_get_current_user_id_from_token
from error import AccessError, InputError


def message_send(token, channel_id, message):
    if token not in database["active_tokens"]:
        raise AccessError("not logged in")

    user_id = auth_get_current_user_id_from_token(token)

    channel = None
    for ch in database["channels"]:
        if ch["id"] == channel_id:
            channel = ch
            break

    if channel is None:
        raise InputError(f"invalid channel id {channel_id}")

    if user_id not in channel["all_members_id"]:
        raise AccessError(
            f"user {user_id} needs to be a member of this channel to send a message"
        )

    channel["message_id_head"] += 1

    new_message = {
        "message_id": channel["message_id_head"],
        "u_id": user_id,
        "message": message,
        "time_created": time.time(),
    }

    # we store the newest messages first
    channel["messages"].insert(0, new_message)

    return {
        # broken!
    }


def message_remove(token, message_id):
    return {}


def message_edit(token, message_id, message):
    return {}
