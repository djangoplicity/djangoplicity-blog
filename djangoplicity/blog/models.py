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

from __future__ import unicode_literals
import copy

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import signals
from django.template import Engine, Template
from django.template.base import TemplateSyntaxError

from djangoplicity.archives.base import ArchiveModel, cache_handler
from djangoplicity.media.models import Image
from djangoplicity.translation.fields import TranslationManyToManyField, TranslationForeignKey
from djangoplicity.translation.models import TranslationModel, translation_reverse
from django.utils.translation import ugettext_lazy as _
from djangoplicity.blog.validators import validate_string_template
from djangoplicity.metadata.models import Program

class BlogTranslationProxyMixin(object):
    def validate_unique(self, exclude=None):
        # Note: We are not using the clean method from the TranslationProxyMixin
        # because it doesn't consider the case when the translation PK(Slug) is manually filled or the ID is numeric
        """ Validate that translation language is *not* identical to source language. """
        try:
            if not self.source:
                raise ValidationError("Blog: You must provide a translation source.")
            if self._state and self._state.adding:
                self.__class__.objects.get(source=self.source.pk, lang=self.lang)
                raise ValidationError({'lang': ["Blog: Translation already exists for selected language."]})
        except ObjectDoesNotExist:
            pass
        super(BlogTranslationProxyMixin, self).validate_unique(exclude=exclude)


class Author(models.Model):
    name = models.CharField(max_length=100)
    biography = models.TextField(blank=True)
    photo = models.ForeignKey(
        Image, blank=True, null=True,
        help_text='Image from the archive',
        on_delete=models.SET_NULL
    )
    static_photo = models.CharField(
        max_length=200, blank=True,
        help_text='Direct link to a JPG image, recommended size: 350px wide'
    )

    def __str__(self):
        return self.name

    @staticmethod
    def post_save_handler(sender, instance, **kwargs):
        for post in instance.post_set.all():
            cache_handler(Post, instance=post)


class AuthorDescription(models.Model):
    '''
    Provides more description about an author for a given post, e.g.:
    "Author: ", or "Interview with", etc.
    '''
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    description = models.CharField(
        max_length=100, blank=True,
        help_text='Optional description, e.g.: "Author: ", or "Interview with"'
    )

    def __str__(self):
        return self.description + ' ' + self.author.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(
        blank=False, unique=True,
        help_text='Slug of the category, used for URLs'
    )
    footer = models.TextField(
        blank=True, help_text='Optional footer added to the bottom of posts'
    )

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    @staticmethod
    def post_save_handler(sender, instance, **kwargs):
        for post in instance.post_set.all():
            cache_handler(Post, instance=post)


class Post(ArchiveModel, TranslationModel):
    slug = models.SlugField(primary_key=True, help_text='Used for the URL, this cannot be updated later')
    title = models.CharField(max_length=255)
    subtitle = models.CharField(
        max_length=255, blank=True,
        help_text='Optional subtitle'
    )
    banner = TranslationForeignKey(Image, verbose_name='Banner Image', null=True, on_delete=models.SET_NULL)
    authors = TranslationManyToManyField('Author', through='AuthorDescription')
    category = TranslationForeignKey('Category', null=True, on_delete=models.SET_NULL)
    tags = TranslationManyToManyField('Tag', blank=True)
    lede = models.TextField()
    body = models.TextField(validators=[validate_string_template])
    discover_box = models.TextField(blank=True)
    numbers_box = models.TextField(blank=True)
    profile = models.TextField(blank=True)
    links = models.TextField(blank=True)
    is_e_and_e = models.BooleanField( default=False, verbose_name=_('Is E&E'), help_text=_('Check this if the post is for the special E&E category and newsletter') )
    programs = TranslationManyToManyField(Program, blank=True, only_sources=True)

    class Meta:
        ordering = ('-release_date', )

    class Translation:
        fields = ['title', 'subtitle', 'lede', 'body', 'discover_box', 'numbers_box', 'profile', 'links']
        excludes = ['published', 'last_modified', 'created']
        non_default_languages_in_fallback = False  # Don't show non-en post. if no en translation is available

    class Archive:
        # No blog specific archive

        class Meta:
            idfield = 'slug'
            release_date = True
            last_modified = True
            created = True
            published = True
            rename_pk = ('blog_post', 'slug')
            rename_fks = (
                ('blog_post', 'source_id'),
                ('blog_authordescription', 'post_slug'),
                ('blog_post_tags', 'post_slug'),
                ('blog_post_programs', 'post_slug'),
            )
            clean_html_fields = ['body', 'discover_box', 'numbers_box', 'profile', 'links']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        '''
        Remove unicode non-breaking white-spaces as they mess up the
        template tags
        '''
        if '\xa0' in self.body:
            self.body = self.body.replace('\xa0', ' ')
        super(Post, self).save(*args, **kwargs)

    @property
    def main_visual(self):
        '''
        {% opengraph_image %} expects a main_visual attribute
        '''
        return self.banner

    def test_render_errors(self):
        '''
        Tries to render the body, return None if everything is fine
        or the error so it can be displayed in the admin
        '''
        # In production the template Engine has debug set to False, but as
        # we need it to identify any possible rendering errors we copy it
        # and set the copies debug to True
        engine = copy.copy(Engine.get_default())
        engine.debug = True

        try:
            Template(self.body, engine=engine)
        except TemplateSyntaxError as e:
            return e.template_debug

    def get_absolute_url(self):
        post = self.get_source()
        return translation_reverse('blog_detail', args=[post.slug], lang=self.lang)

    def og_title(self):
        '''
        Open Graph title
        '''
        title = 'Blog: ' + self.title
        if self.subtitle:
            title += ' ' + self.subtitle
        return title


# ========================================================================
# Translation proxy model,
# The BlogTranslationProxyMixin must be before Post, otherwise it's super() methods doesn't work correctly
# ========================================================================
class PostProxy(BlogTranslationProxyMixin, Post):
    """
    Post proxy model for creating admin only to edit
    translated objects.
    """
    objects = Post.translation_objects

    def __str__(self):
        return self.title

    class Meta:
        proxy = True
        verbose_name = _('Post translation')

    def get_absolute_url(self):
        post = self.get_source()
        return translation_reverse('blog_detail', args=[post.slug], lang=self.lang)


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(
        blank=False, unique=True,
        help_text='Slug of the tag, used for URLs'
    )

    def __str__(self):
        return self.name


signals.post_save.connect(Author.post_save_handler, sender=Author)
signals.post_save.connect(Category.post_save_handler, sender=Category)
