import pytest
import os
import twitter
import datetime, time
from mock import Mock, patch
import simplejson as json
from utils.common import json2obj, DbEngine
from app.models import TwitterToken, TwitterRateState
import app.cs_logger
import app.connections.twitter_connect

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR  = os.path.join(TEST_DIR, "../")
ENV = os.environ['CS_ENV'] = "test"

db_session = DbEngine(os.path.join(TEST_DIR, "../", "config") + "/{env}.json".format(env=ENV)).new_session()
log = app.cs_logger.get_logger(ENV, BASE_DIR)

def truncate_twitter_tables():
    for table in (TwitterRateState, TwitterToken):
        db_session.query(table).delete()
        db_session.commit()

def setup_function(function):
    truncate_twitter_tables()

def teardown_function(function):
    truncate_twitter_tables()

@patch('twitter.Api', autospec=True)
@patch('twitter.ratelimit.RateLimit', autospec=True)
def test_load_tokens(mock_rate_limit, mock_twitter):

    config_path = os.path.join(BASE_DIR, "config", "twitter_configuration_" + ENV + ".json")
    token_path = json.load(open(config_path,'r'))['key_path']
    log.info(f'token_path is: {token_path}')
    print(token_path)
    token_file_names = os.listdir(token_path)

    db_session.rollback()
    conn = app.connections.twitter_connect.TwitterConnect(log, db_session)
    tokens_in_db = db_session.query(TwitterToken).all()
    db_session.commit()
    len_files, len_db = len(token_file_names), len(tokens_in_db)
    print(f'there are {len_files} tokens in files')
    print(f'there are {len_db} tokens in db')
    assert len_files == len_db

@patch('twitter.Api', autospec=True)
def test_twitter_connect_friends(mock_twitter):
    t = mock_twitter.return_value
    conn = app.connections.twitter_connect.TwitterConnect(log, db_session)

    #assert len(conn.rate_limit_resources.values()), 3

    friend_accounts = []# NOTE: # NOTE:
    with open("{script_dir}/fixture_data/twitter_get_friends.json".format(script_dir=TEST_DIR)) as f:
        fixture = json.loads(f.read())
        for account in fixture:
            json_dump = json.dumps(account)
            account_obj = json2obj(json_dump)
            friend_accounts.append(account_obj)

    t.GetFriends.return_value = friend_accounts

    # some gynamstics because Mock overides __name__
    getfriends = conn.api.GetFriends
    getfriends.__name__ = 'GetFriends'

    friends = conn.query(conn.api.GetFriends)
    assert len(friends)  == len(friend_accounts)

@patch('twitter.Api', autospec=True)
@patch('twitter.ratelimit.RateLimit', autospec=True)
def test_exception_retry(mock_rate_limit, mock_twitter):
    #TODO: In the unlikelihood that a VERY slow machine is running these tests
    # you can increase the timedelta here and below to microseconds=500
    reset_time = (datetime.datetime.now() + datetime.timedelta(seconds=1))
    mock_rate_limit.resources = {"getfriends":{"/friends/list":{
        "reset":time.mktime(reset_time.timetuple()),
        "remaining":0,
        "limit":15}}} #num queries per period

    t = mock_twitter.return_value
    t.rate_limit = mock_rate_limit
    t.VerifyCredentials.return_value = True
    t.InitializeRateLimit.return_value = True

    conn = app.connections.twitter_connect.TwitterConnect(log, db_session)

    # some gynamstics because Mock overides __name__
    getfriends = conn.api.GetFriends
    getfriends.__name__ = 'GetFriends'

    friend_accounts = []
    with open("{script_dir}/fixture_data/twitter_get_friends.json".format(script_dir=TEST_DIR)) as f:
        fixture = json.loads(f.read())
        for account in fixture:
            json_dump = json.dumps(account)
            account_obj = json2obj(json_dump)
            friend_accounts.append(account_obj)

    # set the side-effect of get friends to first throw an error, then later return the right result_ttl
    # the reason it does this is that we except GetFriends should be called twice, first to experience the Error
    # and then secondly to assume we roll-over to a good key and then return the right results
    t.GetFriends.side_effect = [twitter.error.TwitterError([{'code': 88, 'message': 'Rate limit exceeded'}]), friend_accounts]
    # assert we are using the first token
    assert conn.endpoint_tokens[conn.curr_endpoint].user_id == 1
    # now try and get friends
    # NOTE! this should call GetFriends twice, because connect should catch an error and then retry


    friends = conn.query(conn.api.GetFriends)
    # assert right results still came throught
    assert len(friends)  == len(friend_accounts)
    # assert that we did roll-over onto the second token
    assert conn.endpoint_tokens[conn.curr_endpoint].user_id == 2
    # OK, so at this point in the code we assume that the second token is active

    #
    # ## now make it wait to go back to the previous key
    # # by setting the second token's reset time to be later - aka further into the future - than the fetch_twitter_snapshot_and_tweets
    # # and also by setting remaining to be zero
    # # because the circumstances we're mocking are that every key is exhausted
    # # so the token that has the shortest time-to-reset is used
    # t.GetFriends.side_effect = [twitter.error.TwitterError([{'code': 88, 'message': 'Rate limit exceeded'}]), friend_accounts]
    # mock_rate_limit.resources = {"getfriends":{"/friends/list":{
    #     "reset":time.mktime((datetime.datetime.now() + datetime.timedelta(seconds=1)).timetuple()),
    #     "remaining":0,
    #     "limit":15}}}
    # t.rate_limit = mock_rate_limit
    #
    # # assert we're still on key 2
    # assert conn.endpoint_tokens[conn.curr_endpoint].user_id == 2
    # # assert (reset_time - datetime.datetime.now()).total_seconds() > 0
    # # make GetFriends run twice again, the first time erroring -- triggering a retry
    # friends = conn.query(conn.api.GetFriends)
    # # assert the right result came back
    # assert len(friends)  == len(friend_accounts)
    # # assert that we correctly went back to token 1
    # # the token with the shortest reset time
    # assert conn.endpoint_tokens[conn.curr_endpoint].user_id == 1
    # #assert (reset_time - datetime.datetime.now()).total_seconds() < 0
    #
    # #TODO test not-only that in the all-exhausted case that rotation happens
    # # but also that query waits until the reset time of the next available token
