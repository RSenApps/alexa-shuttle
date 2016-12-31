from __future__ import print_function
import urllib
import xml.etree.ElementTree as ET

name_to_stop = {'kendall': '01', 'mccormick': '61', 'm.i.t. media lab': '60', 'media lab': '60', 'kresge oval': '61', 'fanew': '51', 'burton': '16', 'simmons hall': '47', 'amherst at wadsworth': '07', 'w 98 at vassar street': '67', 'massy hall': '61', 'kresge turnaround': '61', 'tang hall': '51', 'macgregor': '16', 'the sponge': '47', 'massy': '61', 'next': '51', 'westgate': '51', 'amherst street at wadsworth': '07', 'burton house': '16', 'vassar at mass': '52', 'mccormick hall': '61', 'stata': '48', 'w 92 at amesbury street': '57', 'w 92': '57', 'w 98': '67', 'vassar street at mass ave': '52', 'next house': '51', 'kendall square': '01', 'new house': '51', 'tang': '51', 'macgregor house': '16', 'vassar street at massachusetts avenue': '52', 'baker house': '16', 'simmons': '47', 'kresge': '61', 'stata center': '48', 'burton conner': '16', 'baker': '16'}
name_to_route = {'tech': 'tech', 'tech shuttle': 'tech', 'saferide campus': 'saferidecampshut', 'saferide campus shuttle': 'saferidecampusshut'} 

base_url = "http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=mit"

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "Simmons Shuttles - " + title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_predictions(stop, route=None):
    if route != None:
        url = base_url + '&r=' + name_to_route[str(route.lower())] + '&stopId=' + name_to_stop[str(stop.lower())]
    else:
        url = base_url + '&stopId=' + name_to_stop[str(stop.lower())]

    data = ET.fromstring(urllib.urlopen(url).read())
    stop_name = data[0].attrib['stopTitle']
    predictions = []

    for a in xrange(len(data)):
        if 'dirTitleBecauseNoPredictions' not in data[a].attrib:
            predictions.append((data[a].attrib['routeTitle'], data[a][0][0].attrib['minutes']))

    predictions.sort(key=lambda tup: int(tup[1]))
    print(predictions)
    return (stop_name, predictions)
        

def get_next_shuttle(intent, session):
    card_title = "Next Shuttle"
    speech_output = ''

    """
    if 'value' in intent['slots']['Route']:
        predictions = get_predictions(intent['slots']['Stop']['value'], intent['slots']['Route']['value'])
    else:
        predictions = get_predictions(intent['slots']['Stop']['value'])
    """

    predictions = get_predictions('simmons')

    if len(predictions[1]) == 0:
        speech_output = "There are no shuttles from {} right now.".format(predictions[0])
    else:
        for p in predictions[1]:
            speech_output += "The next {} arrives in {} minute{}. ".format(p[0], p[1], '' if p[1] == '1' else 's')
    
    reprompt_text = speech_output

    return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, True))
    

# --------------- Events ------------------

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetNextShuttle":
        return get_next_shuttle(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return on_help(intent_request, session)
    else:
        raise ValueError("Invalid intent")

def on_help(launch_request, session):
    """ Called when the user requests help
    """

    card_title = "Welcome to Simmons Shuttles"
    speech_output = "Welcome to Simmons Shuttles. You can request upcoming shuttles by asking, when is the next shuttle. All upcoming shuttles will be returned, with the soonest to arrive coming first."
    reprompt_text = "You can request upcoming shuttles by asking, when is the next shuttle. All upcoming shuttles will be returned, with the soonest to arrive coming first."
    
    return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.066c65ca-3fd7-472b-afa9-5208bd634e94"):
        raise ValueError("Invalid Application ID")

    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "LaunchRequest":
        return get_next_shuttle(event['request'], event['session'])
