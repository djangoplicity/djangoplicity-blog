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


from djangoplicity.archives.contrib.queries.defaults import CategoryQuery

from django.db.models import Q

from datetime import datetime

from djangoplicity.archives.contrib.queries import AllPublicQuery
from djangoplicity.metadata.archives.queries import ProgramPublicQuery


class PostTagQuery(CategoryQuery):
    '''
    We override the queryset from the default CategoryQuery to
    exclude embargoed items
    '''
    def queryset( self, model, options, request, stringparam=None, **kwargs ):
        qs, categories = super(PostTagQuery, self).queryset(model, options, request, stringparam)

        return (qs.filter(Q(release_date__lte=datetime.now()) | Q(release_date__isnull=True)), categories)


class PostsAllPublicQuery(AllPublicQuery):
    '''
    Query to hide is_e_and_e posts
    '''
    def queryset(self, model, options, request, **kwargs):
        (qs, query_data) = super(PostsAllPublicQuery, self).queryset(model, options, request, **kwargs)
        qs = qs.filter(is_e_and_e=False)
        return (qs, query_data)
    

class PostsEAndEQuery(AllPublicQuery):
    '''
    Query to show only is_e_and_e posts
    '''
    def queryset(self, model, options, request, **kwargs):
        (qs, query_data) = super(PostsEAndEQuery, self).queryset(model, options, request, **kwargs)
        qs = qs.filter(is_e_and_e=True)
        return (qs, query_data)


class PostsProgramsQuery(ProgramPublicQuery):
    '''
    Query to filter posts by program, excluding is_e_and_e posts
    '''
    def queryset(self, model, options, request, **kwargs):
        (qs, query_data) = super(PostsProgramsQuery, self).queryset(model, options, request, **kwargs)
        qs = qs.filter(is_e_and_e=False)
        return (qs, query_data)