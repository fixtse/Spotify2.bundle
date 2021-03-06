from routing import route_path
from utils import LF
from view import ViewBase, COLUMNS

import locale
import urllib


class SpotifySearch(ViewBase):
    def run(self, query, callback, type='all', count=COLUMNS, plain=False):
        query = urllib.unquote_plus(query)
        count = int(count)

        Log('Search query: "%s", type: %s, count: %s, plain: %s' % (query, type, count, plain))
        placeholders = self.use_placeholders()

        @self.sp.search(query, type, count=count)
        def on_search(result):
            callback(self.build(result, query, type, count, plain, placeholders))

    def build(self, result, query, type, count, plain, placeholders=False):
        oc = ObjectContainer(
            title2=self.get_title(type),
            content=self.get_content(type)
        )

        if result:
            # Fill with results for each media type
            for type in result.media_types:
                self.fill(result, oc, query, count, plain, placeholders, type)

            if len(oc):
                return oc

        return MessageContainer(
            header=L("MSG_TITLE_NO_RESULTS"),
            message=LF("MSG_BODY_NO_RESULTS", query)
        )

    def fill(self, result, oc, query, count, plain, placeholders, type):
        items = getattr(result, type)
        total = getattr(result, '%s_total' % type)

        if not items or not len(items):
            return

        if not plain:
            oc.add(self.get_header(total, query, type))

        self.append_items(oc, items, count, plain, placeholders)

    @classmethod
    def get_header(cls, total, query, type):
        key = route_path('search', query=query, type=type, count=50, plain=True)

        title = '%s (%s)' % (
            cls.get_title(type, True),
            locale.format('%d', total, grouping=True).replace('\xa0', ' ')
        )

        return DirectoryObject(
            key=key,
            title=title,
            thumb=cls.get_thumb(type)
        )

    @staticmethod
    def get_title(type, plain=False):
        title = ""

        if type == 'artists':
            title = L('ARTISTS')
        elif type == 'albums':
            title = L('ALBUMS')
        elif type == 'tracks':
            title = L('TRACKS')
        elif type == 'playlists':
            title = L('PLAYLISTS')

        if title and plain:
            return title
        elif title:
            return "%s - %s" % (L('RESULTS'), title)

        return L('RESULTS')

    @staticmethod
    def get_content(type):
        if type == 'artists':
            return ContainerContent.Artists

        if type == 'albums':
            return ContainerContent.Albums

        if type == 'tracks':
            return ContainerContent.Tracks

        if type == 'playlists':
            return ContainerContent.Playlists

        return ContainerContent.Mixed

    @staticmethod
    def get_thumb(type):
        if type == 'artists':
            return R('icon-artists.png')

        if type == 'albums':
            return R('icon-albums.png')

        if type == 'tracks':
            return R('icon-tracks.png')

        if type == 'playlists':
            return R('icon-playlists.png')
