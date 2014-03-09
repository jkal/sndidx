import re, json, operator
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from webapp.models import idx, col, queries
from webapp.forms import SearchForm
from webapp.helpers import *

import scipy
from pyechonest import config, track
config.ECHO_NEST_API_KEY = 'FILLMEUP'


def signin(request):
    return render(request, 'signin.html')


@login_required
def home(request):
    form = SearchForm()
    return render(request, 'index.html', {
        'form': form
    })


@login_required
def search(request):
    """
    Find songs by searching on their fields.

    Query Mongo to get all matching documents. Return the ID, title
    and artist values of each match.
    """
    query_dict = {}
    for k, v in request.GET.iteritems():
        if v:
            query_dict[k] = re.compile('.*%s.*' % v, re.IGNORECASE)

    res = col.find(query_dict, {
        'song_id': 1, 'title': 1, 'artist': 1
    })

    return render(request, 'results.html', {
        'results': [i for i in res]
    })
    

@require_POST
@login_required
def upload(request):
    """
    Handle the upload of the query file and store it in Mongo.
    """
    f = request.FILES.get('files[]')
    k = request.POST.get('k', 1)

    # Send file to Echonest and request full analysis.
    # Only MP3 supported for now.
    # TODO: This is a bit unstable with large files.
    try:
        tr = track.track_from_file(f, 'mp3')
        tr.get_analysis()
    except EchoNestException:
        return HttpResponse(status=500)

    # Create object to store.
    q = {
        'id': tr.id,
        'md5': tr.md5,
        'bitrate': tr.bitrate,
        'codestring': tr.codestring,
        'duration': tr.duration,
        'energy': tr.energy,
        'segments': tr.segments,
    }

    queries.insert(q)
    redirect_to = reverse('results', args=[tr.md5]) + '?k=' + k

    response = JSONResponse([{
        'name': f.name,
        'url': redirect_to,
    }], {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=file.json'

    return response


@login_required
def results(request, code):
    k = int(request.GET.get('k', 1))

    query = queries.find_one({
        'md5': code
    })

    if not query:
        raise Http404

    segments = query['segments']

    all_song_ids = []
    q_timbre_values = []
    q_loudness_values = []
    q_pitch_values = []

    for segment in segments:
        loudness = segment['loudness_max']
        timbre = scipy.array(segment['timbre']).var()
        pitch = scipy.array(segment['pitches']).mean()

        q_timbre_values.append(timbre)
        q_loudness_values.append(loudness)
        q_pitch_values.append(pitch)

        bbox = (
            timbre, loudness, pitch,
            timbre, loudness, pitch
        )

        nearest = idx.nearest(bbox, 1, objects=True)
        node_ids = [x.object for x in nearest]
        all_song_ids.extend(node_ids)

    # Drop duplicates.
    ids = set(all_song_ids)

    # Fetch the nearest documents from Mongo.
    res = col.find({
        'song_id': {'$in': list(ids)}
    }, {
        'song_id': 1, 'title': 1, 'artist': 1, 'features': 1
    })

    # Compute distances.
    results = []
    for doc in res:
        features = doc['features']
        timbre_values = map(lambda x: x['timbre'], features)
        loudness_values = map(lambda x: x['loudness'], features)
        pitch_values = map(lambda x: x['pitch'], features)

        # Calculate distances
        timbre_dis = distance(timbre_values, q_timbre_values)
        loudness_dis = distance(loudness_values, q_loudness_values)
        pitch_dis = distance(pitch_values, q_pitch_values)

        doc['timbre_dis'] = timbre_dis
        doc['loudness_dis'] = loudness_dis
        doc['pitch_dis'] = pitch_dis
        doc['all'] = (timbre_dis * pitch_dis) + 100*loudness_dis

        results.append(doc)

    sorted_res = sorted(results, key=operator.itemgetter('all'))

    return render(request, 'results_content.html', {
        'results': sorted_res[:k],
        'query': query
    })


def graph_song(request, id):
    res = col.find_one({
        'song_id': id
    }, {
        'features': 1
    })

    if not res:
        raise Http404

    features = res['features']

    pitch_data = []
    timbre_data = []
    loudness_data = []

    for i, segment in enumerate(features):
        x = segment['start']
        pitch = segment['pitch']
        timbre = segment['timbre']
        loudness = segment['loudness']

        pitch_data.append({'x': x, 'y': pitch})
        timbre_data.append({'x': x, 'y': timbre})
        loudness_data.append({'x': x, 'y': loudness})

    return render(request, 'graph.html', {
        'pitch_data': json.dumps(pitch_data),
        'timbre_data': json.dumps(timbre_data),
        'loudness_data': json.dumps(loudness_data),
    })
        

def graph_query(request, id):
    res = queries.find_one({
        'id': id
    }, {
        'segments': 1
    })

    if not res:
        raise Http404

    segments = res['segments']

    pitch_data = []
    timbre_data = []
    loudness_data = []

    for i, segment in enumerate(segments):
        x = segment['start']
        pitch = scipy.array(segment['pitches']).mean()
        timbre = scipy.array(segment['timbre']).var()
        loudness = segment['loudness_max']

        pitch_data.append({'x': x, 'y': pitch})
        timbre_data.append({'x': x, 'y': timbre})
        loudness_data.append({'x': x, 'y': loudness})

    return render(request, 'graph.html', {
        'pitch_data': json.dumps(pitch_data),
        'timbre_data': json.dumps(timbre_data),
        'loudness_data': json.dumps(loudness_data),
    })


def graph(request, id):
    if id.startswith('SO'):
        return graph_song(request, id)
    else:
        return graph_query(request, id)
