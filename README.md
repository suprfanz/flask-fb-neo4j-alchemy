# SuprFanz.com Tutorial: Importing Data from Facebook into Neo4j for Alchemy Data Visualizaion Step by Step

The purpose of this lab is connect to the Facebook API using python and import Event data into 
[Neo4j](https://neo4j.com/) and present the data in a simple attractive graph visualization via [Alchemy JS](http://graphalchemist.github.io/Alchemy/#/). 

## Getting Started

To get started download/clone this project and set up a project in your favorite IDE.

### Facebook

You need an access token to make a call to the Facebook API to pull data, so you obtain one by logging into your website with Facebook. 

You will need to set up and connect your own [Facebook app](https://developers.facebook.com/docs/apps/register) in the settings in Views.py. Make sure the URL that you are using to run the application is the one in your Facebook application Settings > Basic > 
Site URL. It is not recommended that you change any other oAuth or website settings or add anymore URLs anywhere except in special cases.

If you're running the project locally, you have to use an IP address. Facebook won't let you use "localhost" but you can have a port number.

```
# Facebook app details
FB_APP_ID = '###############'
FB_APP_NAME = 'SuprFanz Data Visualization Demo'
FB_APP_SECRET = '###################################'
# Fill in ### with your own app details

```
The access token is obtained from the Facebook cookie and then stored in the session dict and the database upon login to be used in API calls later.

### Neo4j 

You can download and set up your own local instance of [Neo4j](https://neo4j.com/download/?ref=home) or run Neo4j in the [Neo4j Sandbox](https://neo4j.com/sandbox-v2/). Connect your Neo4j database in config.py
```
# Database details
neo4j_password = '########'
neo4j_admin = 'neo4j'
neo4j_dbip = '###.###.##.##'
# Fill in ### with your own db details
```

When you enter an event in the form, guest and event nodes and their relationships will be created in your database. It's best to start with a clean database dedicated to this project.

### Python 3.x and Flask

This project is based on the [Facebook SDK Flask Example](https://github.com/mobolic/facebook-sdk/tree/master/examples/flask). Install Python 3.x. Pip install requirements to a virtualenv
```
pip install -r requirements
```
To import Facebook events there is an option to use the FacebookEvents class or just the individual functions in run_get_facebook_event.py. The project is set up to use the class by default but some people prefer not to.

The class is called with:
```
    event_id = facebook_event_id
    token = facebook_token
    facebookevents = FacebookEvents(event_id, token)
    facebookevents.get_facebook_event()
    facebookevents.get_event_owner()
    facebookevents.get_rsvps()
```

If you don't use the class, change the import statement in views.py from

```
from app.facebookevent.run_get_facebook_event_class import FacebookEvents
```

to 

```
from app.facebookevent.run_get_facebook_event import get_facebook_event_main
```
then call the function with 

```
get_facebook_event_main(event_id, token)
```

Both need to be passed the Facebook event id and a valid access token.

The Facebook event ID is in the URL for a Facebook event and is a unique identifier Facebook uses for events. It is not always the same length. The JavaScript form validation ensures that this ID is what gets passed into the Python function rather than the whole URL.
```
https://www.facebook.com/events/###############/
# The ### is the event ID
```

The script graphjson.py converts your Neo4j data to D3 json to be used in the D3 visualization. It creates a json file in static/data. You will need to change the path to your own local or server path

    with open(
            "C:\\Users\\yourusername\\Documents\\path\\to\\neo4j2d3\\app\\static\\data\\neo4j2d3_new.json",
            "w") as f:
        f.write(graphjson)
        
This file gets overwritten every time the page is loaded when the user is logged in to ensure the latest data from the database is used. If you have a large amount of data, it might slow performance, in which case you could disable or move this function (main()) from the main view.
 
 ```
 @app.route('/')
def index():
    # If a user was set in the get_current_user function before the request,
    # the user is logged in.
    if g.user:
        main()
        # converts the neo4j data into graphjson
        return render_template('index.html', app_id=FB_APP_ID,
                               app_name=FB_APP_NAME, user=g.user)

```
The required json format is basically a flat list of nodes and then a flat list of links(edges). The links must have a source and target that correspond to the nodes they're related to. See fb_events_bak.json for an example of the correct json format
```
{
  "nodes": [
    {
      "nodeType": "guest",
      "name": "Person's Name",
      "id": "###############"
    }
  ],
  "edges": [
    {
      "rsvp": "attending",
      "target": "###############",
      "source": "###############"
    }
  ]
}
```

You can modify the [Cypher](https://neo4j.com/developer/cypher-query-language/) queries to your particular data set as long as the resulting json is in the correct format.

```
def create_guest_node():
    # fetches the guest nodes from neo4j
    insert_query_guest = '''
    MATCH (a:fb_guest)
    WITH collect({name: a.fb_guest_name, nodeType:'guest', id:a.fb_usr_id}) AS nodes RETURN nodes
    '''
```

The JavaScript relies on the properties 'nodeType', 'id' and 'name' for nodes and for edges 'source', 'target', and 'rsvp'. If you change the property names in your database, you will have to change the corresponding properties in graphjson.py and the javascript in index.html to ensure the new names are mapped correctly.


## Running

The application will create event and guest nodes and relationships using the Facebook events that you import. Therefore specific property key values are expected. Your database should be empty the first time you run it. 

1. Start Neo4J. 
2. Run the application run.py. 
3. Open your website URL in the latest Chrome on desktop (other browsers not yet supported).
4. Click the login button. There will be a Facebook popup. Login in using your Facebook account.
5. Accept the permissions the application asks for the first time (public profile)
6. Once the popup closes, the page should automatically reload, but if it doesn't, refresh.
7. Copy and paste a Facebook event URL into the form and press Import
8. You will see a visualization of the data. If you use a very large event, this could take a minute or more to load.
9. When you click on the nodes, you will see information and a Facebook picture of the person the node corresponds to and all that node's relationships.
10. You can click on the edges to see the edge type and the nodes it's related to.

### Options

Display and other options can be set in the Alchemy config in the javascript in index.html. You may wish to set "forceLocked" to true when you have a lot of nodes as they can get quite busy and harder to work with on screen. "afterload" is where you can add your own callback functions that fire after the graph is loaded.

```
config = {
                "backgroundColor": "#FFFFFF",
                "dataSource": dataSource,
                "nodeTypes": {"nodeType": ["guest", "event"]},
                "nodeCaption": "name",
                "forceLocked": false,
                "directedEdges": true,
                "alpha": 0.001,
                "edgeArrowSize": 10,
                graphHeight: function () {
                    return (windowHeight * 0.95);
                },
                graphWidth: function () {
                    return (windowWidth * 0.95);
                },
                "nodeStyle": {
                    "guest": {
                        "radius": 12,
                        "borderWidth": 0,
                        "color": "#90caf9",
                        "selected": {
                            "borderColor": "#CCC",
                            "borderWidth": 6,
                            "radius": 18,
                            "opacity": 0.5
                        },
                        "highlighted": {
                            "borderColor": "#90caf9",
                            "borderWidth": 5
                        }
                    },
                    "event": {
                        "radius": 25,
                        "borderWidth": 0,
                        "color": "#fdd835",
                        "selected": {
                            "borderColor": "#CCC",
                            "borderWidth": 6
                        },
                        "highlighted": {
                            "borderColor": "#FFFFFF",
                            "borderWidth": 5
                        }
                    }
                },
                "edgeCaption": "rsvp",
                "edgeTypes": {"rsvp": ["not_replied", "unsure", "attending"]},
                "edgeStyle": {
                    "not_replied": {
                        "width": 1,
                        "color": "#CCCCCC",
                        "opacity": 0.5,
                        "selected": {
                            "width": 3,
                            "opacity": 1
                        },
                        "highlighted": {
                            "color": "#BBBBBB",
                            "width": 3,
                            "opacity": 1
                        }
                    },
                    "unsure": {
                        "width": 2,
                        "color": "#ffa726",
                        "opacity": 0.5,
                        "highlighted": {
                            "width": 3,
                            "opacity": 1
                        },
                        "selected": {
                            "width": 5,
                            "opacity": 1
                        }
                    },
                    "attending": {
                        "width": 2,
                        "color": "#b2ff59",
                        "opacity": 0.5,
                        "highlighted": {
                            "opacity": 1,
                            "width": 3
                        },
                        "selected": {
                            "opacity": 1,
                            "width": 5
                        }
                    }
                },
                afterLoad: showinfo
            };
        // Initialize Alchemy
        alchemy = new Alchemy(config);
```
For more options, see [Alchemy JS](http://graphalchemist.github.io/Alchemy/#/) docs and examples

## Notes
This app does not yet contain a test to check if the Facebook event is valid, only that the URL passes the regex. This does not take into account when a user added an event and then later cancelled it or when the URL otherwise passes the regex but still does not match an existing event. There still needs to be an API request that throws an exception when the request is a 404 in the validation process. This is planned for a future release.

Private events are not currently supported as this require extending the app permissions which would call for a [Facebook review](https://developers.facebook.com/docs/facebook-login/overview). The assumption is that only the default public profile permissions are requested. A developer could change this in the [permissions scope](https://developers.facebook.com/docs/facebook-login/permissions/requesting-and-revoking) requested to allow for their own private events data to be pulled and no review would be required if the app was in developer test mode.

In the Facebook Graph API the edge "unsure" is used to describe people who have responded to an event as either "Maybe" or "Interested".

## Built With

* [Neo4j](https://neo4j.com/) - Non-relational Graph database
* [Python](https://www.python.org/) - programming language.
* [Flask](https://rometools.github.io/rome/) - a microframework for Python
* [Alchemy JS](http://graphalchemist.github.io/Alchemy/#/) - A graph visualization api based on D3

## Contributing

We welcome contributions to this project and are open to ideas. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Ray Bernard** - [@SuprFanz](https://github.com/suprfanz)
* **Jen Webb** - [@jenwebb](https://github.com/jenwebb)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [Facebook-SDK](https://github.com/mobolic/facebook-sdk/tree/master/examples/flask)
* [GraphAlchemist](https://github.com/GraphAlchemist/Alchemy)

