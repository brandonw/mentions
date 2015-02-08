from django.utils import timezone
from models import SearchSite, SearchRun, SiteRun, Match


# This task assumes it has been triggered by an authorized user.
def search(search_id):
    search_sites_query = SearchSite.objects \
        .filter(search__id=search_id) \
        .filter(search__is_enabled=True) \
        .filter(site__is_enabled=True) \
        .select_related('search', 'site')

    if not search_sites_query.exists():
        return

    search_sites = [search_site for search_site in search_sites_query.all()]
    search_run = SearchRun.objects.create(
        search=search_sites[0].search, start_time=timezone.now())
    keywords = [kw for kw in
                search_site.search.keywords.filter(is_enabled=True).all()]

    for search_site in search_sites:
        site_run = SiteRun.objects.create(
            start_time=timezone.now(), site=search_site.site,
            search_run=search_run)

        matches = []
        # TODO: Depending on the site, the preference would be to use an
        # existing API to parse content. Possible fallback would be manually
        # scraping content. Keywords may be able to integrated more directly,
        # depending on the social site. For example, the twitter search focus
        # only (or more heavily) on hashtagged items, as opposed to the rest of
        # a tweet's content.

        # dummy match
        matches.append(Match(
            title='test match', url=search_site.site.url,
            src_keyword=keywords[0], found_keyword=kw.keyword + '1',
            site_run=site_run))
        # end dummy match

        # add matches all at once to reduce db load
        site_run.match_set.add(*matches)
        site_run.finish_time = timezone.now()
        site_run.save()
        search_run.siterun_set.add(site_run)

    search_run.finish_time = timezone.now()
    search_run.save()


# This task assumes it has been triggered by an authorized user.
def export_matches(match_ids, email, attachment_base_name):
    matches = Match.objects \
        .filter(id__in=match_ids)
    for match in matches.all():
        # add row to csv
        pass

    # send e-mail
