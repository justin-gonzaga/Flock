import sys
from json import dumps
from flask import Flask, request, jsonify
from flask_cors import CORS
from error import InputError

# Import the functions we are wrapping
from auth import auth_login, auth_logout, auth_register
from user import (
    user_profile,
    user_profile_setname,
    user_profile_setemail,
    user_profile_sethandle,
)

from channels import channels_create, channels_create, channels_list, channels_listall
from channel import channel_details, channel_messages, channel_join, channel_leave
from message import message_send, message_remove, message_edit
from channel import (
    channel_details,
    channel_messages,
    channel_join,
    channel_invite,
    channel_leave,
    channel_invite,
    channel_removeowner,
    channel_addowner,
)
from standup import standup_start, standup_active, standup_send
from other import clear, users_all, search
from other import clear, admin_userpermission_change


def defaultHandler(err):
    response = err.get_response()
    print("response", err, err.get_response())
    response.data = dumps(
        {
            "code": err.code,
            "name": "System Error",
            "message": err.get_description(),
        }
    )
    response.content_type = "application/json"
    return response


APP = Flask(__name__)
CORS(APP)

APP.config["TRAP_HTTP_EXCEPTIONS"] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=["GET"])
def echo():
    data = request.args.get("data")
    if data == "echo":
        raise InputError(description='Cannot echo "echo"')
    return dumps({"data": data})


# Clear database
@APP.route("/clear", methods=["DELETE"])
def delete():
    clear()
    return dumps({})


# Auth functions
@APP.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    return dumps(auth_login(data["email"], data["password"]))


@APP.route("/auth/logout", methods=["POST"])
def logout():
    data = request.get_json()
    return dumps(auth_logout(data["token"]))


@APP.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    return dumps(
        auth_register(
            data["email"], data["password"], data["name_first"], data["name_last"]
        )
    )


# Message functions
@APP.route("/message/edit", methods=["PUT"])
def edit_message():
    data = request.get_json()
    message_edit(data["token"], data["message_id"], data["message"])
    return jsonify({})


@APP.route("/message/remove", methods=["DELETE"])
def remove_message():
    data = request.get_json()
    return jsonify(message_remove(data["token"], data["message_id"]))


@APP.route("/message/send", methods=["POST"])
def send_message():
    data = request.get_json()
    return jsonify(
        message_send(data["token"], int(data["channel_id"]), data["message"])
    )


# User functions
@APP.route("/user/profile", methods=["GET"])
def profile():
    token = request.args.get("token")
    u_id = request.args.get("u_id")
    return dumps(user_profile(token, int(u_id)))


@APP.route("/user/profile/setname", methods=["PUT"])
def setname():
    data = request.get_json()
    user_profile_setname(data["token"], data["name_first"], data["name_last"])


@APP.route("/user/profile/setemail", methods=["PUT"])
def setemail():
    data = request.get_json()
    user_profile_setemail(data["token"], data["email"])


@APP.route("/user/profile/sethandle", methods=["PUT"])
def sethandle():
    data = request.get_json()
    user_profile_sethandle(data["token"], data["handle_str"])


@APP.route("/users/all", methods=["GET"])
def get_all():
    token = request.args.get("token")
    return dumps(users_all(token))


# Channels functions
@APP.route("/channels/create", methods=["POST"])
def channels_create_handler():
    data = request.get_json()

    token = data["token"]
    name = data["name"]
    is_public = data["is_public"]

    return jsonify(channels_create(token, name, is_public))


@APP.route("/channels/list", methods=["GET"])
def list_channels():
    # Lists the channels an authorised user is a part of
    token = request.args.get("token")
    return jsonify(channels_list(token))


# Channel functions
@APP.route("/channel/invite", methods=["POST"])
def channel_invite_handler():
    data = request.get_json()

    token = data["token"]
    channel_id = int(data["channel_id"])
    user_id = data["u_id"]

    return jsonify(channel_invite(token, channel_id, user_id))


@APP.route("/channel/details", methods=["GET"])
def channel_details_handler():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    return jsonify(channel_details(token, channel_id))


@APP.route("/channels/listall", methods=["GET"])
def channel_listall():
    token = request.args.get("token")
    return jsonify(channels_listall(token))


@APP.route("/channel/join", methods=["POST"])
def join_channel():
    data = request.get_json()
    return jsonify(channel_join(data["token"], data["channel_id"]))


@APP.route("/channel/messages", methods=["GET"])
def messages_channel():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    start = int(request.args.get("start"))

    return jsonify(channel_messages(token, channel_id, start))


@APP.route("/channel/leave", methods=["POST"])
def channel_leave_handler():
    data = request.get_json()
    return jsonify(channel_leave(data["token"], int(data["channel_id"])))


@APP.route("/channel/addowner", methods=["POST"])
def channel_addowner_handler():
    data = request.get_json()

    token = data["token"]
    channel_id = int(data["channel_id"])
    u_id = data["u_id"]

    return jsonify(channel_addowner(token, channel_id, u_id))


@APP.route("/channel/removeowner", methods=["POST"])
def channel_removeowner_handler():
    data = request.get_json()

    token = data["token"]
    channel_id = int(data["channel_id"])
    u_id = data["u_id"]

    return jsonify(channel_removeowner(token, channel_id, u_id))


@APP.route("/admin/userpermission/change", methods=["POST"])
def admin_userpermission_change_handler():
    data = request.get_json()

    token = data["token"]
    u_id = data["u_id"]
    permission_id = data["permission_id"]

    return jsonify(admin_userpermission_change(token, u_id, permission_id))


@APP.route("/search", methods=["GET"])
def search_messages_handler():
    token = request.args.get("token")
    query_str = request.args.get("query_str")

    return jsonify(search(token, query_str))


# Standup functions
@APP.route("/standup/start", methods=["POST"])
def standup_start_handler():
    data = request.get_json()

    token = data["token"]
    channel_id = data["channel_id"]
    length = data["length"]

    return jsonify(standup_start(token, channel_id, length))

@APP.route("/standup/active", methods=["GET"])
def standup_active_handler():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))

    return jsonify(standup_active(token, channel_id))

@APP.route("/standup/send", methods=["POST"])
def standup_send_handler():
    data = request.get_json()

    token = data["token"]
    channel_id = data["channel_id"]
    message = data["message"]

    return jsonify(standup_send(token, channel_id, message))

if __name__ == "__main__":
    APP.run(port=0)  # Do not edit this port
