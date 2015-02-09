from django.conf.urls import patterns, url
from mentions import views

urlpatterns = patterns(
    '',

    # START SEARCH #

    # * Paginated list of all enabled searches owned by the current user.
    # * Can be ordered by a GET sort parameter.
    # * Can also be filtered by a keyword.
    # * Provides an edit link for each search.
    # * Provides a deletion link for each search.
    url(r'^search/$',
        views.SearchListView.as_view(),
        name='search-list'
        ),

    # * Displays a brief summary of the search
    # * Displays a small form whose POST request triggers the search to be
    #   manually run.
    # * Displays a paginated list of associated runs.
    # * Each run has a link to a pre-filtered list of matches
    url(r'^search/(?P<slug>[\w-]+)/$',
        views.SearchDetailView.as_view(),
        name='search-detail'
        ),

    # * Edits an existing search.
    # * Allows the search attributes to be modified.
    # * Allows keywords to be added or removed. Keywords handled via a simple
    #   textbox input, and parsed out in the server. That way new keywords can
    #   be added inline, without requiring navigation to a separate keyword
    #   creation page.
    # * Any new keywords added will ensure the user is set to the current user.
    url(r'^search/(?P<slug>[\w-]+)/edit/$',
        views.SearchEditView.as_view(),
        name='search-edit'
        ),

    # * Deletes an existing search by setting is_enabled=False.
    url(r'^search/(?P<slug>[\w-]+)/delete/$',
        views.SearchDeleteView.as_view(),
        name='search-delete'
        ),

    # * Creates a new search, specifying keywords inline.
    # * Ensures the current user is set as the new search's user field, as well
    #   as any new keywords' user fields.
    url(r'^search/create/$',
        views.SearchCreateView.as_view(),
        name='search-create'
        ),

    # END SEARCH #

    # START KEYWORD #

    # * Paginated list of all enabled keywords owned by the current user.
    # * For each keyword, render a link to a pre-filtered list of searches
    #   using this keyword.
    # * For each keyword, render a link to a pre-filtered list of matches of
    #   this keyword.
    # * For each keyword, render a delete link that disables usage of this
    #   keyword in all related searches.
    url(r'^keyword/$',
        views.KeywordListView.as_view(),
        name='keyword-list',
        ),

    # * Displays the keyword.
    # * Displays a paginated list of all searches that use this keyword.
    url(r'^keyword/(?P<slug>[\w-]+)/$',
        views.KeywordDetailView.as_view(),
        name='keyword-detail'
        ),

    # * Deletes a keyword (prevents its use from all related searches)
    url(r'^keyword/(?P<slug>[\w-]+)/delete/$',
        views.KeywordDeleteView.as_view(),
        name='keyword-delete'
        ),

    # END KEYWORD #

    # START MATCHES #

    # * Displays a paginated list of all matches across all search runs of the
    #   current user.
    # * Can be ordered by the date of the related run, or by the run itself.
    # * Can be filtered by keyword, site, or run.
    # * Inline form allowing an arbitrary list of matches to be exported to csv
    #   and e-mailed to the user.
    url(r'^matches/$',
        views.MatchListView.as_view(),
        name='match-list'
        ),

    # END MATCHES #

    # START TRIGGERS #

    # * Manually triggers the search task on a higher priority queue, to
    #   account with the speed implied in manually running a search.
    url(r'^search/(?P<pk>\d+)/execute/$',
        views.trigger_search,
        name='search-trigger'
        ),

    # * Triggers the export task on the POSTed list of match IDs.
    url(r'^matches/export/$',
        views.trigger_export,
        name='export-trigger'
        ),

    # END TRIGGERS #
)
