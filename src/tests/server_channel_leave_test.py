import requests
from test_helpers import url, http_register_n_users

###########################################################################
#                       Tests for channel/leave                           #
###########################################################################

# User with invalid token tries to leave a channel
def test_leave_invalid_token(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # User creates a channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()

    # User leaves channel with invalid token
    response = requests.post(
        url + "channel/leave",
        json={"token": -1, "channel_id": channel["channel_id"]},
    )

    assert response.status_code == 403


# User leaves public channel successfully
def test_leave_channel_successfully(url):
    requests.delete(url + "clear")
    owner = http_register_n_users(url, 1)

    # Owner creates public channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Owner leaves the channel so the channel is empty
    requests.post(
        url + "channel/leave",
        json={"token": owner["token"], "channel_id": channel["channel_id"]},
    )

    # Response should return error 403 as owner no longer has access
    response = requests.get(
        url + "channel/details",
        params={"token": owner["token"], "channel_id": channel["channel_id"]},
    )
    assert response.status_code == 403


# A user tries to leave a private channel that they are not part of
def test_non_member_leave_channel_private(url):
    requests.delete(url + "clear")
    owner, non_member = http_register_n_users(url, 2)

    # Owner creates a private channel
    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    # Non-member tries to leave channel they are not part of
    response = requests.post(
        url + "channel/leave",
        json={
            "token": non_member["token"],
            "channel_id": private_channel["channel_id"],
        },
    )

    assert response.status_code == 403


# A user tries to leave a public channel that they are not part of
def test_non_member_leave_channel_public(url):
    requests.delete(url + "clear")
    owner, member = http_register_n_users(url, 2)
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    response = requests.post(
        url + "channel/leave",
        json={"token": member["token"], "channel_id": channel["channel_id"]},
    )

    assert response.status_code == 403


# User tries to leave channel with invalid channel id
def test_leave_channel_id_invalid(url):
    requests.delete(url + "clear")
    owner = http_register_n_users(url, 1)

    # Owner creates public channel
    requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    )

    # Owner tries to leave channel with invalid channel_id
    invalid_channel_id = -1
    response = requests.post(
        url + "channel/leave",
        json={"token": owner["token"], "channel_id": invalid_channel_id},
    )

    assert response.status_code == 400