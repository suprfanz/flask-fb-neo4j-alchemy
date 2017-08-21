# -*- coding: utf-8 -*-
"""
This Class pulls event and rsvp into neo4j via the Facebook API.
Written by Ray Bernard
"""
import requests
import json
from neo4j.v1 import GraphDatabase, basic_auth
from config import neo4j_password, neo4j_dbip


def get_facebook_event(fb_event_id, fb_token):
    # get the event from facebook and put into neo4j
    session = GraphDatabase.driver("bolt://{}:7687".format(neo4j_dbip),
                                   auth=basic_auth("neo4j", "{}".format(neo4j_password))).session()
    url = 'https://graph.facebook.com/v2.10/{}'.format(fb_event_id)
    parameters = {'access_token': fb_token}
    r = requests.get(url, params=parameters)
    result = json.loads(r.text)
    print(result)
    fb_event_name = result['name']
    fb_event_id = result['id']

    try:
        fb_event_description = result['description']
    except:
        fb_event_description = ''
    fb_event_start_time = result['start_time']

    insert_query = '''
    MERGE (n:fb_event{fb_event_id:{fb_event_id},description:{description},event_name:{event_name},start_time:{start_time}})
    '''
    session.run(insert_query, parameters={"fb_event_id": fb_event_id, "description": fb_event_description,
                                          "event_name": fb_event_name, "start_time": fb_event_start_time
                                          })
    session.close()


# Create host node
def get_event_owner(fb_event_id, fb_token):
    # get the host from facebook and put into neo4j
    session = GraphDatabase.driver("bolt://{}:7687".format(neo4j_dbip),
                                   auth=basic_auth("neo4j", "{}".format(neo4j_password))).session()
    url = 'https://graph.facebook.com/v2.7/{}/?fields=owner'.format(fb_event_id)
    parameters = {'access_token': fb_token}
    r = requests.get(url, params=parameters)
    result = json.loads(r.text)
    print(result)
    host_name = result['owner']['name']
    host_id = result['owner']['id']
    insert_query = '''
    MERGE (n:host{host_name:{host_name},host_id:{host_id}})
    '''
    insert_query_rel = '''
    MATCH (n:host),(n1:fb_event)
    WHERE n.host_id = {host_id} AND n1.fb_event_id = {fb_event_id}
    MERGE (n)-[r:HOST]->(n1)
    SET r.source = {host_id}
    SET r.target = {fb_event_id}
    '''
    session.run(insert_query, parameters={"host_name": host_name,
                                          "host_id": host_id
                                          })

    session.run(insert_query_rel, parameters={"host_id": host_id,
                                              "fb_event_id": fb_event_id
                                              })
    session.close()


def get_rsvps(fb_event_id, fb_token):
    # get the event guests from facebook and put into neo4j
    session = GraphDatabase.driver("bolt://{}:7687".format(neo4j_dbip),
                                   auth=basic_auth("neo4j", "{}".format(neo4j_password))).session()
    # Connect to Facebook Graph Api
    url = 'https://graph.facebook.com/v2.7/{}/attending?limit=5000'.format(fb_event_id)
    parameters = {'access_token': fb_token}
    r = requests.get(url, params=parameters)
    results = json.loads(r.text)

    # Query to create guest in neo4j
    insert_query = '''
    MERGE(n:fb_guest{fb_usr_id:{fb_usr_id},fb_guest_name: {fb_guest_name}})
    '''

    # Query create a relationshiop between guest and event
    insert_query_rel_create = '''
    MATCH (n:fb_guest),(n1:fb_event)
    WHERE n.fb_usr_id = {fb_usr_id} AND n1.fb_event_id = {fb_event_id}
    MERGE (n)-[r:RSVP]->(n1)
    SET r.rsvp_status = {rsvp_status}
    SET r.source = {fb_usr_id}
    SET r.target = {fb_event_id}
    SET r.value = {value}
    '''

    for index, record in enumerate(results['data']):
        fb_guest_name = record['name']
        fb_usr_id = record['id']
        rsvp_status = record['rsvp_status']

        session.run(insert_query,
                    parameters={"fb_usr_id": fb_usr_id,
                                "fb_guest_name": fb_guest_name,
                                "fb_event_id": fb_event_id
                                })

        session.run(insert_query_rel_create,
                    parameters={"fb_usr_id": fb_usr_id,
                                "fb_guest_name": fb_guest_name,
                                "fb_event_id": fb_event_id,
                                "rsvp_status": rsvp_status,
                                "value":3
                                })
        print(rsvp_status + ' ' + str(fb_guest_name) + ' ' + str(fb_usr_id) + ' ' + str(fb_event_id))


    url = 'https://graph.facebook.com/v2.7/{}/interested?limit=5000'.format(fb_event_id)
    parameters = {'access_token': fb_token}
    r = requests.get(url, params=parameters)
    results = json.loads(r.text)

    for index, record in enumerate(results['data']):
        fb_guest_name = record['name']
        fb_usr_id = record['id']
        rsvp_status = record['rsvp_status']

        print('interested = ' + str(fb_guest_name))

        session.run(insert_query,
                    parameters={"fb_usr_id": fb_usr_id,
                                "fb_guest_name": fb_guest_name,
                                "fb_event_id": fb_event_id
                                })

        session.run(insert_query_rel_create,
                    parameters={"fb_usr_id": fb_usr_id,
                                "fb_guest_name": fb_guest_name,
                                "fb_event_id": fb_event_id,
                                "rsvp_status": rsvp_status,
                                "value": 2
                                })


    url = 'https://graph.facebook.com/v2.7/{}/noreply?limit=5000'.format(fb_event_id)
    parameters = {'access_token': fb_token}
    r = requests.get(url, params=parameters)
    results = json.loads(r.text)
    for index, record in enumerate(results['data']):
        fb_guest_name = record['name']
        fb_usr_id = record['id']
        rsvp_status = record['rsvp_status']
        print('noreply = ' + str(fb_guest_name))

        session.run(insert_query,
                    parameters={"fb_usr_id": fb_usr_id,
                                "fb_guest_name": fb_guest_name,
                                "fb_event_id": fb_event_id})

        # This creates the relation from guest to event
        session.run(insert_query_rel_create,
                    parameters={"fb_usr_id": fb_usr_id,
                                "fb_guest_name": fb_guest_name,
                                "fb_event_id": fb_event_id,
                                "rsvp_status": rsvp_status,
                                "value": 1
                                })
    session.close()


def get_facebook_event_main(fb_event_id, fb_token):
    get_facebook_event(fb_event_id, fb_token)
    get_event_owner(fb_event_id, fb_token)
    get_rsvps(fb_event_id, fb_token)


if __name__ == "__main__":
    event_id = '1876887819229907'
    token = 'EAAB1QyM77aUBALbfDkmw3iPRtiL6eZCwZCtNBiJvwjW0e9QJKnZCRfgEJwFZByY0Cdny7YWiGk1OoHdEVzJ3wYQxZBFVWZCBpsqkxcOZCx6taVig8ZCB95zdZBIsx3YqofDrPD7ya44TFM7MgN0Eea0RGNWiL4EmiZBlXOeDcY3dkfBcJdSZCp2dJYjsikaMB4hTDcQZCK5MHJYPogZDZD'
    get_facebook_event_main(event_id, token)
