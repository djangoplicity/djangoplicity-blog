# -*- coding: utf-8 -*-
#
# eso-blog
# Copyright (c) 2007-2017, European Southern Observatory (ESO)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#   * Neither the name of the European Southern Observatory nor the names
#     of its contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
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

from djangoplicity.archives.feeds import DjangoplicityArchiveFeed
from django.conf import settings
from djangoplicity.blog.models import Post
from djangoplicity.blog.options import PostOptions
from djangoplicity.archives.utils import get_resource_size

BLOG_TITLE = settings.BLOG_TITLE if hasattr( settings, 'BLOG_TITLE' ) else 'Blog'
BLOG_DESCRIPTION = settings.BLOG_DESCRIPTION if hasattr( settings, 'BLOG_DESCRIPTION' ) else ''

class PostFeed(DjangoplicityArchiveFeed):
    title = BLOG_TITLE
    description = BLOG_DESCRIPTION
    description_template = 'feeds/post_description.html'
    link = '/public/blog/'

    class Meta(DjangoplicityArchiveFeed.Meta):
        model = Post
        options = PostOptions
        latest_fieldname = Post.Archive.Meta.release_date_fieldname
        enclosure_resources = { '': 'resource_screen' }
        default_query = PostOptions.Queries.default
        items_to_display = 10

    def item_enclosure_url(self, item):
        if item.banner and item.banner.resource_screen:
            return item.banner.resource_screen.absolute_url
        return None

    def item_enclosure_length(self, item):
        if item.banner and item.banner.resource_screen:
            size = get_resource_size(item.banner, item.banner.resource_screen)
            if not getattr(item.banner.resource_screen, 'is_from_content_server', False) and not item.banner.resource_screen.closed:
                item.banner.resource_screen.close()
            return size
        return None

    def item_enclosure_mime_type(self, item):
        return 'image/jpeg'
