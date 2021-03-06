import pytest
from channels import channels_create, channels_list, channels_listall
from channel import channel_details
from database import clear_database
from error import InputError, AccessError
from auth import auth_register, auth_login

def test_create_invalid_token():
    clear_database()
    with pytest.raises(AccessError):
        channels_create(-1, "channel name", is_public=False)

def test_create_simple():
    clear_database()
    user = register_and_login_user()
    channel = channels_create(user['token'], 'channel_name', is_public=True)

    details = channel_details(user['token'], channel['channel_id'])
    assert details['name'] == 'channel_name'

def test_create_private():
    clear_database()
    usera = auth_register("email@a.com", "averylongpassword", "first", "last")
    userb = auth_register("email@b.com", "averylongpassword", "firstb", "lastb")
    channel = channels_create(usera['token'], 'channel', is_public=False)

    details = channel_details(usera['token'], channel['channel_id'])
    assert details['name'] == 'channel'

    with pytest.raises(AccessError):
        channel_details(userb['token'], channel['channel_id'])

def test_long_name_error():
    clear_database()
    user = register_and_login_user()
    with pytest.raises(InputError):
        channels_create(user['token'], 'channel name longer than twenty char', True)

def test_empty_name():
    clear_database()

    user = auth_register("email@a.com", "averylongpassword", "first", "last")
    channel_id = channels_create(user['token'], "", is_public=True)['channel_id']
    details = channel_details(user['token'], channel_id)
    assert details['name'] == 'new_channel'


def test_creator_becomes_owner_and_member():
    clear_database()
    user = register_and_login_user()
    channel = channels_create(user['token'], 'channel', is_public=True)
    details = channel_details(user['token'], channel['channel_id'])

    assert len(details['owner_members']) == 1
    assert details['owner_members'][0]['u_id'] == user['u_id']

    assert len(details['all_members']) == 1
    assert details['all_members'][0]['u_id'] == user['u_id']

# Helper function that registers a user and logs them in
# Returns {u_id, token}
def register_and_login_user():
    auth_register('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_01_credentials = auth_login('validemail01@gmail.com', 'validpass@!01')
    return user_01_credentials

def test_channels_list_invalid_token():
    clear_database()
    user = register_and_login_user()
    token = user['token']
    name = 'channel'  
    channels_create(token, name, is_public=True)['channel_id']
    invalid_token = -1
    
    with pytest.raises(AccessError):
        assert channels_list(invalid_token)

def test_channels_list_public():
    clear_database()
    user = register_and_login_user()
    token = user['token']
    name = 'channel'
    channel_id = channels_create(token, name, is_public=True)['channel_id']
    authorised_channels = [{'channel_id': channel_id, 'name': name}]
    assert channels_list(token) == authorised_channels

def test_channels_list_private():
    clear_database()
    user = register_and_login_user()
    token = user['token']
    name = 'channel'
    channel_id = channels_create(token, name, is_public=False)['channel_id']
    authorised_channels = [{'channel_id': channel_id, 'name': name}]
    assert channels_list(token) == authorised_channels

def test_channels_list_multiple_public():
    clear_database()
    user = register_and_login_user()
    token = user['token']
    channel_ids = []
    names = ['public_channel_01', 'public_channel_02', 'public_channel_03']
    for name in names:
        channel_ids.append(channels_create(token, name, is_public=True)['channel_id'])

    authorised_channels = []
    for channel_id, name in zip(channel_ids, names):
        authorised_channels.append({'channel_id': channel_id, 'name': name})
    assert channels_list(token) == authorised_channels

def test_channels_list_multiple_private():
    clear_database()
    user = register_and_login_user()
    token = user['token']
    channel_ids = []
    names = ['private_channel_01', 'private_channel_02', 'private_channel_03']
    for name in names:
        channel_ids.append(channels_create(token, name, is_public=False)['channel_id'])

    authorised_channels = []
    for channel_id, name in zip(channel_ids, names):
        authorised_channels.append({'channel_id': channel_id, 'name': name})
    assert channels_list(token) == authorised_channels

def register_and_login_multiple_users(email, password, first_name, last_name):
    auth_register(email, password, first_name, last_name)
    user_credentials = auth_login(email, password)
    return user_credentials

def test_channels_list_unauthorised_multiple_public():
    clear_database()

    user_01 = register_and_login_multiple_users('01@gmail.com', 'validpass@!01', 'First', 'User')
    user_02 = register_and_login_multiple_users('02@gmail.com', 'valpass@!02', 'Second', 'User')
    user_03 = register_and_login_multiple_users('03@gmail.com', 'valpass@!03', 'Third', 'User')
    channel_id_01 = channels_create(user_01['token'], 'channel1', is_public=True)['channel_id']
    channel_id_02 = channels_create(user_02['token'], 'channel2', is_public=True)['channel_id']
    channel_id_03 = channels_create(user_03['token'], 'channel3', is_public=True)['channel_id']

    assert channels_list(user_01['token']) == [{'channel_id': channel_id_01, 'name': 'channel1'}]
    assert channels_list(user_02['token']) == [{'channel_id': channel_id_02, 'name': 'channel2'}]
    assert channels_list(user_03['token']) == [{'channel_id': channel_id_03, 'name': 'channel3'}]

def test_channels_list_unauthorised_multiple_private():
    clear_database()

    user_01 = register_and_login_multiple_users('01@gmail.com', 'validpass@!01', 'First', 'User')
    user_02 = register_and_login_multiple_users('02@gmail.com', 'validpass@!02', 'Second', 'User')
    user_03 = register_and_login_multiple_users('03@gmail.com', 'validpass@!03', 'Third', 'User')
    channel_id_01 = channels_create(user_01['token'], 'channel1', is_public=False)['channel_id']
    channel_id_02 = channels_create(user_02['token'], 'channel2', is_public=False)['channel_id']
    channel_id_03 = channels_create(user_03['token'], 'channel3', is_public=False)['channel_id']

    assert channels_list(user_01['token']) == [{'channel_id': channel_id_01, 'name': 'channel1'}]
    assert channels_list(user_02['token']) == [{'channel_id': channel_id_02, 'name': 'channel2'}]
    assert channels_list(user_03['token']) == [{'channel_id': channel_id_03, 'name': 'channel3'}]

def test_channels_list_empty():
    clear_database()
    user_01 = register_and_login_multiple_users('email01@gmail.com', 'pass@!01', 'First', 'User')
    assert channels_list(user_01['token']) == []

def test_channels_listall_invalid_token():
    clear_database()
    user = register_and_login_user()
    token = user['token']
    name = 'channel'  
    channels_create(token, name, is_public=True)['channel_id']
    invalid_token = -1
    
    with pytest.raises(AccessError):
        assert channels_listall(invalid_token)

def test_channels_listall_empty():
    clear_database()
    user_01 = register_and_login_multiple_users('email01@gmail.com', 'pass@!01', 'First', 'User')
    assert channels_listall(user_01['token']) == []

def test_channels_listall_public():
    clear_database()
    user_01 = register_and_login_multiple_users('email01@gmail.com', 'pass@!01', 'First', 'User')
    token = user_01['token']

    channel_ids = []
    names = ['public_channel_01', 'public_channel_02', 'public_channel_03']
    for name in names:
        channel_ids.append(channels_create(token, name, is_public=True)['channel_id'])

    authorised_channels = []
    for channel_id, name in zip(channel_ids, names):
        authorised_channels.append({'channel_id': channel_id, 'name': name})
    assert channels_listall(token) == authorised_channels

def test_channels_listall_private():
    clear_database()
    user_01 = register_and_login_multiple_users('email01@gmail.com', 'pass@!01', 'First', 'User')
    token = user_01['token']

    channel_ids = []
    names = ['private_channel_01', 'private_channel_02', 'private_channel_03']
    for name in names:
        channel_ids.append(channels_create(token, name, is_public=False)['channel_id'])

    authorised_channels = []
    for channel_id, name in zip(channel_ids, names):
        authorised_channels.append({'channel_id': channel_id, 'name': name})
    assert channels_listall(token) == authorised_channels

def test_channels_listall_multiple_users_public():
    clear_database()

    user_01 = register_and_login_multiple_users('email01@gmail.com', 'pass@!01', 'First', 'User')
    user_02 = register_and_login_multiple_users('email02@gmail.com', 'pass@!02', 'Second', 'User')
    user_03 = register_and_login_multiple_users('email03@gmail.com', 'pass@!03', 'Third', 'User')

    tokens = [user_01['token'], user_02['token'], user_03['token']]
    channel_ids = []
    names = ['private_channel_01', 'private_channel_02', 'private_channel_03']
    for name, token in zip(names, tokens):
        channel_ids.append(channels_create(token, name, is_public=True)['channel_id'])

    authorised_channels = []
    for channel_id, name in zip(channel_ids, names):
        authorised_channels.append({'channel_id': channel_id, 'name': name})

    assert channels_listall(user_01['token']) == authorised_channels
    assert channels_listall(user_02['token']) == authorised_channels
    assert channels_listall(user_03['token']) == authorised_channels

def test_channels_listall_multiple_users_private():
    clear_database()

    user_01 = register_and_login_multiple_users('email01@gmail.com', 'pass@!01', 'First', 'User')
    user_02 = register_and_login_multiple_users('email02@gmail.com', 'pass@!02', 'Second', 'User')
    user_03 = register_and_login_multiple_users('email03@gmail.com', 'pass@!03', 'Third', 'User')

    tokens = [user_01['token'], user_02['token'], user_03['token']]
    channel_ids = []
    names = ['private_channel_01', 'private_channel_02', 'private_channel_03']
    for name, token in zip(names, tokens):
        channel_ids.append(channels_create(token, name, is_public=False)['channel_id'])

    authorised_channels = []
    for channel_id, name in zip(channel_ids, names):
        authorised_channels.append({'channel_id': channel_id, 'name': name})

    assert channels_listall(user_01['token']) == authorised_channels
    assert channels_listall(user_02['token']) == authorised_channels
    assert channels_listall(user_03['token']) == authorised_channels
    