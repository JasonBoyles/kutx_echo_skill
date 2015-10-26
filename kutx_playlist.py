import json
import requests


def lambda_handler(event, context):
    print json.dumps(event)
    print 'track info is:\n{}'.format(json.dumps(track_info()))
    print "checking request type..."
    if event['request']['type'] == 'IntentRequest':
        print "request type was IntentRequest"
        return handle_intent(event.get('request'), event.get('session'))


def handle_intent(request, session):
    intent = request.get('intent')
    intent_name = intent.get('name')
    print "handling intent", intent_name
    if intent_name == 'get_current_track':
        return handle_intent_get(request, session)


def handle_intent_get(request, session):
    print "handing get intent..."
    track = track_info()
    response_string = ''
    if track:
        print "we got track info."
        response_string = "this is {}, by artist {}.".format(
            track.get('track'),
            track.get('artist'))
    else:
        print "there was no track info available."
        response_string = "could not get track info."
    print "caling build_response..."
    return build_response(build_speechlet(response_string), session)


def build_response(speechlet, session):
    print "build_response called..."
    response = {
        "version": "1.0",
        "sessionAttributes": session,
        "response": speechlet
    }
    print json.dumps(response, indent=2)
    return response


def build_speechlet(speech):
    print "build_speechlet called..."
    speech_response = {
        "outputSpeech": {
            "type": "PlainText",
            "text": speech
        },
        "card": {
            "type": "Simple",
            "title": "kutx song",
            "content": speech
        },
        "shouldEndSession": True
    }
    return speech_response


def now_playing(station_ucs='50ef24ebe1c8a1369593d032'):
    url = "https://api.composer.nprstations.org/v1/widget/{}/now".format(
        station_ucs)
    r = requests.get(url, params={'format': 'json'})
    if r.status_code == 200:
        return r.json()
    else:
        r.raise_for_status()


def track_info():
    try:
        on_now = now_playing().get('onNow', {})
        track = on_now.get('song', {})
        if track:
            track_name = track.get('trackName')
            artist_name = track.get('artistName')
            print 'track is', track.get('trackName'), '-', \
                track.get('artistName')  # onNow.trackName
            return {'artist': artist_name, 'track': track_name}
        else:
            print "there was no track info."
            return {}
    except requests.exceptions.HTTPError as oops:
        print "sorry, there was an error:", oops
        return None


if __name__ == '__main__':
    track_info()
