# -*- coding: utf-8 -*-
#
# eso-blog
# Copyright (c) 2007-2017, European Southern Observatory (ESO)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the European Southern Observatory nor the names
#      of its contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY ESO ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL ESO BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE

from django.utils.translation import ugettext_noop as _

from djangoplicity.archives.contrib.browsers import ListBrowser, SerializationBrowser
from djangoplicity.archives.contrib.queries.defaults import AllPublicQuery, \
    EmbargoQuery
from djangoplicity.archives.options import ArchiveOptions

from djangoplicity.blog.queries import PostTagQuery
from djangoplicity.blog.models import Tag
from djangoplicity.blog.views import PostDetailView



from djangoplicity.archives.contrib.queries.defaults import AdvancedSearchQuery
from djangoplicity.archives.contrib.search.fields import DateSinceSearchField, DateUntilSearchField, IdSearchField, TextSearchField
from djangoplicity.archives.contrib.serialization import JSONEmitter
from djangoplicity.archives.views import SerializationDetailView
from .models import Post
from .queries import PostsAllPublicQuery, PostsEAndEQuery, PostsProgramsQuery
from .serializers import PostSerializer


class PostOptions(ArchiveOptions):
    slug_field = 'slug'
    urlname_prefix = 'blog'
    template_name = 'archives/post/detail.html'
    detail_view = PostDetailView
    select_related = ('banner', )
    prefetch_related = ('tags', 'authordescription_set__author')
    search_fields = (
        'slug', 'title', 'subtitle', 'lede', 'body', 'authors__name',
        'category__name_en', 'category__name_es', 'category__slug_en', 'category__slug_es', 'tags__name', 'tags__slug'
    )

    class Queries(object):
        default = AllPublicQuery(browsers=('normal', ), verbose_name=_('Blog Posts'), feed_name='default', select_related=['category'])
        staging = EmbargoQuery(browsers=('normal', ), verbose_name=_('Blog Posts (Staging)'))
        tag = PostTagQuery(browsers=('normal', ), relation_field='tags', url_field='slug', title_field='name', use_category_title=True, verbose_name='%s')
        category = PostTagQuery(browsers=('normal', ), relation_field='category', url_field='slug', title_field='name', use_category_title=True, verbose_name='%s')

    class Browsers(object):
        normal = ListBrowser()

    @staticmethod
    def extra_context( obj, lang=None ):
        return {
            'tags': Tag.objects.order_by('name')
        }

    @staticmethod
    def feeds():
        from djangoplicity.blog.feeds import PostFeed
        return {
            '': PostFeed,
        }


class BlogPostOptions(ArchiveOptions):
    urlname_prefix = 'blogs'

    search_fields = ('slug', 'title', 'lede', 'body')

    class Queries:
        default = PostsAllPublicQuery(browsers=('normal', 'json'), verbose_name=_(("Blog Posts")), feed_name="default")
        e_and_e = PostsEAndEQuery(browsers=('normal', 'json'), verbose_name=_(("E&E Blog Posts")))
        program = PostsProgramsQuery(relation_field='programs', browsers=('normal', 'json'), verbose_name=_(("Blog Posts by Program")))
        search = AdvancedSearchQuery(browsers=('normal', 'json'), verbose_name=_(("Advanced Blog Search")), searchable=False)

    class Browsers:
        normal = ListBrowser(verbose_name=_(('View all')), paginate_by=100)
        json = SerializationBrowser(serializer=PostSerializer, emitter=JSONEmitter, paginate_by=20, display=False, verbose_name=_(("JSON")))

    detail_views = (
        { 'url_pattern': 'api/(?P<serializer>json)/', 'view': SerializationDetailView(serializer=PostSerializer, emitters=[JSONEmitter]), 'urlname_suffix': 'serialization' },
    )

    class AdvancedSearch:
        slug = TextSearchField(label=_(('Post Slug')), model_field='slug')
        published_since = DateSinceSearchField(label=_(("Published since")), model_field='release_date')
        published_until = DateUntilSearchField(label=_(("Published until")), model_field='release_date')
        title = TextSearchField(label=_(("Title")), model_field='title')
        body = TextSearchField(label=_(("Body")), model_field='body')

        class Meta:
            verbose_name = _(("Advanced Blog Search"))
