haystack\_static\_pages
=======================

Haystack Static Pages is an extension library for Haystack.  Currently, it adds
the ability to index static pages through the use of a `settings.py` variable
and command extension.

Dependencies:
------------

This package relies on the BeautifulSoup Python HTML/XML parser which must be installed,
along with haystack and django.

Basic Usage:
------------

#. Setup and install Haystack.
#. Add ``haystack_static_pages`` to your ``INSTALLED_APPS`` in ``settings.py``
#. Add ``HAYSTACK_STATIC_PAGES`` to your ``settings.py``.

#. If you intend to register static pages yourself, stop haystack static pages doing so
by adding ``HAYSTACK_STATIC_PAGES_NO_REGISTER = False`` to your ``settings.py``
#. Set HAYSTACK_STATIC_PAGES_STORE_REL_URL in your settings.py to True if you wish to
store relative URLs rather than absolute URLs (helpful if you have a single site on
different domains.

	eg. ::

	    HAYSTACK_STATIC_PAGES = (
                'static-about_us',                        # A named url
                'static-help',                            # Another named url
                'http://www.example.com/some_page.html',  # A fully qualified url
	    )

#. ``./manage.py syncdb`` to create the necessary tables.
#. ``./manage.py crawl_static_pages`` to populate the database with the static
   page content.  This is needed for Haystack to properly map the urls to the
   content. Output should indicate which pages were crawled and where, as well
   as the total number of pages found.
   **Crawled pages must be accessible through an http connection.  ie., they
   must be viewable in a browser.**
#. ``./manage.py rebuild_index`` to create the search indexes used by Haystack.
   You should see a note about how many static pages were indexed.  The number
   of static pages indexed should match the number of static pages created in
   the step above.

Advanced Usage:
---------------

There are currently two command line options that can be used with the
`crawl_static_pages` command:

-l LANG, --language=LANG  This allows the user to specify the desired language
                          for indexing content.  Each page will include a
                          ``language`` attribute that will correspond to the
                          page's language as detected in the html lang attribute
                          or 'en' if unable to be determined.
-p PORT, --port=PORT      This allows the user to include the port number to
                          crawl, if required.
-n NAMED_URLS, --names=NAMED_URLS
                          This allows the user to include additional named urls
                          that may not necessarily be known for placing in settings.py
-u URLS, --urls=URLS      This allows the user to include additional actual urls
                          that may not necessarily be known for placing in settings.py
-s, --strip=True               Strip tags from the fetched HTML, and only keeps the text content
                          Can also be set by specifying HAYSTACK_STATIC_PAGES_STRIP_HTML=True
                          in your ``settings.py``
