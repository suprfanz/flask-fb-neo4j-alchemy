"""
graphjson module pull an event from neo4j and creates
graphjson formated file to be used with AlchemyJS
Written by Ray Bernard ray@suprfanz.com

"""

import json
from neo4j.v1 import GraphDatabase, basic_auth
from config import neo4j_dbip, neo4j_admin, neo4j_password

session = GraphDatabase.driver("bolt://{}:7687".format(neo4j_dbip),
                               auth=basic_auth("{}".format(neo4j_admin), "{}".format(neo4j_password))).session()


def create_guest_node():
    # fetches the guest nodes from neo4j
    insert_query_guest = '''
    MATCH (a:fb_guest)
    WITH collect({name: a.fb_guest_name, nodeType:'guest', id:a.fb_usr_id}) AS nodes RETURN nodes
    '''

    result = session.run(insert_query_guest)
    for record in result:
        guest_node = json.dumps(dict(record))
        return guest_node


def create_guest_edge():
    # fetches the guest-event edges from neo4j
    insert_query_guest = '''
    MATCH (a:fb_guest)-[r:RSVP]->(b:fb_event)
    WITH collect({source: a.fb_usr_id,target: b.fb_event_id, rsvp:r.rsvp_status}) AS edges RETURN edges
    '''
    result = session.run(insert_query_guest)
    for record in result:
        return json.dumps(dict(record))


def create_event_node():
    # fetches the event nodes from neo4j
    insert_query_guest = '''
    MATCH (b:fb_event)
    WITH collect ({name: b.event_name, nodeType:'event', id:b.fb_event_id}) AS nodes RETURN nodes
    '''

    result = session.run(insert_query_guest)
    for record in result:
        return json.dumps(record['nodes'])


def main():
    # puts the data together in graphjson format
    comment = '{"comment":" This is a test",'

    guest_nodes = str(create_guest_node())[1:][:-2]

    guest_edges = str(create_guest_edge())[1:]

    event_node = str((create_event_node())) + ']'

    graphjson = str(comment) + str(guest_nodes) + ', ' + str(event_node) + ',' + str(guest_edges)

    print(graphjson)
    # put your file path to json data here
    with open(
            "C:\\Users\\yourname\\Documents\\path\\to\\alchemy\\app\\static\\data\\fb_events.json",
            "w") as f:
        f.write(graphjson)
    return graphjson


if __name__ == '__main__':
    main()
