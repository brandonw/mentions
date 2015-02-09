from django.db import models
from autoslug import AutoSlugField
from django.core.urlresolvers import reverse
# Assumes there exists a user model at the path 'users.User'


# BEGIN SEARCH MODELS #

class Site(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = AutoSlugField(populate_from='name')

    url = models.URLField()

    # administrative deletion flag
    is_enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class Keyword(models.Model):

    # If a Keyword should instead be strictly a one-to-many relationship with
    # a Search, then the user field can be removed, as the Search relationship
    # could be traversed to determine the user.
    user = models.ForeignKey('users.User')

    keyword = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique_with='user')

    # user deletion flag
    is_enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return self.keyword


# Searches have a many-to-many relationship with both sites and keywords. This
# allows not only sites to be used across multiple searches, but for the same
# keyword to be used across multiple searches. If the same keyword is used
# across multiple searches, the matches can all be related back to the original
# keyword, despite being used in different searches.
# If this is undesired, the Keyword model could define a standard ForeignKey
# field to the Search, instead of a ManyToMany relationship.
class Search(models.Model):
    user = models.ForeignKey('users.User')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    sites = models.ManyToManyField(Site, through='SearchSite')
    keywords = models.ManyToManyField(Keyword, through='SearchKeyword')

    # user deletion flag
    is_enabled = models.BooleanField(default=True)

    # The run period, in minutes. Leave blank to disable periodic execution
    # and rely on triggering it manually.
    # This assumes the period can be customized per search. if this is not the
    # case, then this field could be changed to a simple boolean of
    # is_scheduled, where if it is set then it is run by the static scheduler
    # configured in the settings. If it is unset, it would only be run when
    # manually triggered.
    run_period = models.PositiveIntegerField(null=True, blank=True)

    # an alias given to this search by the user
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique_with='user')

    class Meta:
        unique_together = (('user', 'name'),)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('search-detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        super(Search, self).save(args, kwargs)
        if self.run_period:
            # TODO: Handle creating/updating the schedule via database-backed
            # django-celery scheduler, if dynamic scheduling is used.
            # Otherwise, this overridden save method can be removed entirely.
            pass


class SearchSite(models.Model):
    site = models.ForeignKey(Site)
    search = models.ForeignKey(Search)

    def __unicode__(self):
        return '{} - {}'.format(self.search.name, self.site.name)


class SearchKeyword(models.Model):
    keyword = models.ForeignKey(Keyword)
    search = models.ForeignKey(Search)

    def __unicode__(self):
        return '{} - {}'.format(self.search.name, self.keyword.keyword)

# END SEARCH MODELS #


# BEGIN RUN MODELS #
class SearchRun(models.Model):
    search = models.ForeignKey(Search)
    start = models.DateTimeField(null=True, blank=True)
    finish = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return '{} @ {}'.format(self.search.name, self.start)


class SiteRun(models.Model):
    search_run = models.ForeignKey(SearchRun)
    site = models.ForeignKey(Site)
    start = models.DateTimeField()
    finish = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return '{} @ {}'.format(self.site.name, self.start)


class Match(models.Model):
    site_run = models.ForeignKey(SiteRun)
    title = models.TextField()  # page titles can be of arbitrary length
    url = models.URLField()
    src_keyword = models.ForeignKey(Keyword)

    # support possibility of the exact phrase that was matched not being the
    # original keyword (conjugations, synonyms, et cetera)
    found_keyword = models.CharField(max_length=255)

    def __unicode__(self):
        return '{} matched "{}"'.format(
            self.site_run.search_run.search.name, self.found_keyword)
# END RUN MODELS #
