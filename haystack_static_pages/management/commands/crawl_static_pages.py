import urllib2, urlparse

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils import translation
from django.utils.html import escape
from optparse import make_option
from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser
from haystack_static_pages.models import StaticPage

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def list_callback(option, opt, value, parser):
  setattr(parser.values, option.dest, value.split(','))


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-p', '--port', action='store', dest='port', default=None,
            help='The port number to use for internal urls.'),
        make_option('-l', '--language', action='store', dest='language', default=None,
            help='The language to use when requesting the page'),
        make_option('-n', '--names', type='string', action='callback', callback=list_callback,
            help='List of named urls to be indexed (in addition to HAYSTACK_STATIC_PAGES)'),
        make_option('-u', '--urls', type='string', action='callback', callback=list_callback,
            help='List of actual urls to be indexed (in addition to HAYSTACK_STATIC_PAGES)'),
        make_option('-s', '--strip', action='store_true', dest='strip_html', default=False,
            help='Strip HTML tags prior to saving the page'),
    )
    help = 'Setup static pages defined in HAYSTACK_STATIC_PAGES for indexing by Haystack'

    def handle(self, *args, **options):
        cmd = 'crawl_static_pages [-p PORT] [-l LANG] [-u LIST OF URLs]'
        if args:
            raise CommandError('Usage is: %s' % cmd)

        self.port = options.get('port')

        if self.port:
            if not self.port.isdigit():
                raise CommandError('%r is not a valid port number.' % self.port)
            else:
                self.port = int(self.port)

        count = 0

        self.language = options.get('language')

        if self.language:
            translation.activate(self.language)

        urls_to_index = list( settings.HAYSTACK_STATIC_PAGES )

        if options.get('urls'): urls_to_index.extend( options.get('urls') )
        if options.get('names'): urls_to_index.extend( options.get('names') )

        for url in urls_to_index:
            if not url.startswith('http://'):
                try:
                    if self.port:
                        url = 'http://%s:%r%s' % (Site.objects.get_current().domain, self.port, reverse(url))
                    else:
                        url = 'http://%s%s' % (Site.objects.get_current().domain, reverse(url))
                except NoReverseMatch:
                    try:
                        url = 'http://%s%s' % (Site.objects.get_current().domain, url)
                        html = urllib2.urlopen(url)
                    except:
                        print 'No reverse match found for named url and is not valid url\n%s' % url
                        continue

            print 'Analyzing %s...' % url

            if not hasattr( settings, 'HAYSTACK_STATIC_PAGES_STORE_REL_URL' ) or \
                not settings.HAYSTACK_STATIC_PAGES_STORE_REL_URL:
                store_url = url
            else:
                store_url = urlparse.urlsplit(url).path

            try:
                page = StaticPage.objects.get(url=store_url)
                print '%s already exists in the index, updating...' % url
            except StaticPage.DoesNotExist:
                print '%s is new, adding...' % url
                page = StaticPage(url=store_url)
                pass

            try:
                html = urllib2.urlopen(url)
            except urllib2.URLError:
                print "Error while reading '%s'" % url
                continue

            soup = BeautifulSoup(html)
            try:
                page.title = escape(soup.head.title.string)
            except AttributeError:
                page.title = 'Untitled'
            meta = soup.find('meta', attrs={'name': 'description'})
            if meta:
                page.description = meta.get('content', '')
            else:
                page.description = ''
            page.language = soup.html.get('lang', u'en-US')
            if options.get('strip_html') or hasattr( settings, 'HAYSTACK_STATIC_PAGES_STRIP_HTML') and settings.HAYSTACK_STATIC_PAGES_STRIP_HTML:
                # remove inline javascript
                [s.extract() for s in soup('script')]
                page.content = strip_tags(unicode(soup.body))
            else:
                page.content = soup.prettify()
            page.save()
            count += 1

        print 'Crawled %d static pages' % count
