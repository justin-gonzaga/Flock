import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channels/list                           #
###########################################################################
# User admin of one channel
def test_channels_list_1_channel(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    channel = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list["channels"]]


# User admin of two chanels
def test_channels_list_2_channels(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    channel01 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()
    channel02 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_02", "is_public": True},
    ).json()

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel01["channel_id"] in [
        x["channel_id"] for x in channels_list["channels"]
    ]
    assert channel02["channel_id"] in [
        x["channel_id"] for x in channels_list["channels"]
    ]


# User admin of private channel
def test_channels_list_public(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    channel = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": False},
    ).json()

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list["channels"]]


# Non-admin requests channels list
def tests_channels_list_non_admin(url):
    requests.delete(url + "clear")
    admin, user = http_register_n_users(url, 2)
    channel = requests.post(
        url + "channels/create",
        json={"token": admin["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list["channels"]]


# User in multiple different channels
def test_channel_list_user_multiple(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # User creates 5 different channels
    channel_01 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()

    channel_02 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_02", "is_public": True},
    ).json()

    channel_03 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_03", "is_public": True},
    ).json()

    channel_04 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_04", "is_public": True},
    ).json()

    channel_05 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_05", "is_public": True},
    ).json()

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list_dict = response.json()["channels"]
    channel_list = [x["channel_id"] for x in channels_list_dict]

    assert channel_01["channel_id"] in channel_list
    assert channel_02["channel_id"] in channel_list
    assert channel_03["channel_id"] in channel_list
    assert channel_04["channel_id"] in channel_list
    assert channel_05["channel_id"] in channel_list


# Channels list with messages and multiple users in channel
def tests_channels_list_large(url):
    requests.delete(url + "clear")
    admin, user01, user02, user03 = http_register_n_users(url, 4)

    channel = requests.post(
        url + "channels/create",
        json={"token": admin["token"], "name": "channel_01", "is_public": True},
    ).json()

    # 3 users join the channel
    r = requests.post(
        url + "channel/join",
        json={"token": user01["token"], "channel_id": channel["channel_id"]},
    )
    assert r.status_code == 200

    r = requests.post(
        url + "channel/join",
        json={"token": user02["token"], "channel_id": channel["channel_id"]},
    )
    assert r.status_code == 200

    r = requests.post(
        url + "channel/join",
        json={"token": user03["token"], "channel_id": channel["channel_id"]},
    )
    assert r.status_code == 200

    # Each user sends a customised message
    r = requests.post(
        url + "message/send",
        json={
            "token": user01["token"],
            "channel_id": channel["channel_id"],
            "message": "user01",
        },
    )
    assert r.status_code == 200

    r = requests.post(
        url + "message/send",
        json={
            "token": user02["token"],
            "channel_id": channel["channel_id"],
            "message": "user02",
        },
    )
    assert r.status_code == 200

    r = requests.post(
        url + "message/send",
        json={
            "token": user03["token"],
            "channel_id": channel["channel_id"],
            "message": "user03",
        },
    )
    assert r.status_code == 200

    # Ensure each user has this channel in their channel list
    response = requests.get(url + "channels/list", params={"token": user01["token"]})
    assert response.status_code == 200
    channels_list_dict = response.json()["channels"]
    channel_list = [x["channel_id"] for x in channels_list_dict]

    assert channel["channel_id"] in channel_list

    response = requests.get(url + "channels/list", params={"token": user02["token"]})
    assert response.status_code == 200
    channels_list_dict = response.json()["channels"]
    channel_list = [x["channel_id"] for x in channels_list_dict]

    assert channel["channel_id"] in channel_list

    response = requests.get(url + "channels/list", params={"token": user03["token"]})
    assert response.status_code == 200
    channels_list_dict = response.json()["channels"]
    channel_list = [x["channel_id"] for x in channels_list_dict]

    assert channel["channel_id"] in channel_list
