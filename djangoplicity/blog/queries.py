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

from django.conf import settings
from djangoplicity.archives.contrib.queries.defaults import CategoryQuery

from django.db.models import Q

from datetime import datetime
if settings.USE_I18N:
    from django.utils import translation

class PostTagQuery(CategoryQuery):
    '''
    We override the queryset from the default CategoryQuery to
    exclude embargoed items
    '''
    def queryset( self, model, options, request, stringparam=None, **kwargs ):
        qs, categories = super(PostTagQuery, self).queryset(model, options, request, stringparam)

        if settings.USE_I18N:
            lang = translation.get_language()
            qs = model.objects.fallback(lang).filter(
                Q(release_date__lte=datetime.now()) | Q(release_date__isnull=True),
                pk__in=qs.values_list('pk', flat=True)
            )
        else:
            qs = qs.filter(
                Q(release_date__lte=datetime.now()) | Q(release_date__isnull=True)
            )

        return qs, categories
