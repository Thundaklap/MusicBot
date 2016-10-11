from concurrent.futures import ThreadPoolExecutor

import functools
import spotipy
import re


class SpotifyIntegration:

    def __init__(self, access_token):
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        self.spotify = spotipy.Spotify(access_token, )

    async def recommend(self, loop, entry, count=5):
        return await loop.run_in_executor(self.thread_pool,
                                          functools.partial(self._recommend_blocking, entry, count))

    def _recommend_blocking(self, entry, count=5):
        # find the first song corresponding to the title, and hope its the right one.
        # if it's not, too bad.

        # make the search term a bit easier for spotify to understand since it cant search for shit
        # without this if theres any weird stuff in the title search wont return anything good
        search_term = entry.title
        search_term = search_term.replace('-', '')
        search_term = search_term.replace('ft.', '')
        search_term = re.sub('\(.+?\)', '', search_term)
        print("Search term: %s" % search_term)
        search_results = self.spotify.search(search_term)

        if 'tracks' not in search_results or 'items' not in search_results['tracks']:
            print('Error getting Spotify recommendation: invalid response.')
            return

        tracks = search_results['tracks']['items']
        if not tracks:
            print('Error getting Spotify recommendation: no tracks found')
            return

        track = tracks[0]
        if 'id' not in track:
            print('Error getting spotify recommendation: invalid response.')
            return

        recommendation_results = self.spotify.recommendations(seed_tracks=[track['id'], ])

        # Youtube search "<song name> <artist>", usually does the trick
        try:
            return [x['name'] + ' ' + x['artists'][0]['name'] for x in recommendation_results['tracks'][:count]]
        except KeyError:
            # fuck off, shouldn't happen
            print('Error in getting artist names for recommendation.')
