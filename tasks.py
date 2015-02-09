from django.utils import timezone
from models import Search, SearchRun, SiteRun, Match, Export


def create_searchrun(search_id):
    search_run = SearchRun.objects.create(search_id=search_id)
    # exec search(search_run.id) as async subtask
    # note that the scheduling of a new search is not idempotent


def search(searchrun_id):
    search_run = Search.objects.get(id=searchrun_id)
    if search_run.start:
        # make search task idempotent by checking if it has been started
        # elsewhere exiting early if so
        return

    search_run.start = timezone.now()
    if not search_run.search.is_enabled:
        search_run.end = timezone.now()
    search_run.save()
    if not search_run.search.is_enabled:
        # exit early if search is disabled
        return

    sites = search_run.search.sites.filter(is_enabled=True)

    if not sites.exists():
        return

    keywords = [kw for kw in search.keywords.filter(is_enabled=True).all()]

    for site in sites.all():
        site_run = SiteRun.objects.create(
            start=timezone.now(), site=site,
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
            title='test match', url=site.url,
            src_keyword=keywords[0], found_keyword=kw.keyword + '1',
            site_run=site_run))
        # end dummy match

        # add matches all at once to reduce db load
        site_run.match_set.add(*matches)
        site_run.finish = timezone.now()
        site_run.save()
        search_run.siterun_set.add(site_run)

    search_run.finish = timezone.now()
    search_run.save()


def export_matches(export_id):
    export = Export.objects.get(id=export_id)
    if export.start:
        # exit early if this export has already begun elsewhere
        return

    for match in export.matches.all():
        # add row to csv
        pass

    # send e-mail
