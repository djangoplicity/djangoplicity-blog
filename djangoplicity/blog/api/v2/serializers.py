from rest_framework import serializers
from djangoplicity.archives.api.v2.serializers import ArchiveSerializerMixin
from djangoplicity.metadata.api.v2.serializers import ProgramSerializer
from djangoplicity.media.api.v2.serializers import ImageMiniSerializer
from djangoplicity.blog.models import Post

class PostMiniSerializer(ArchiveSerializerMixin, serializers.ModelSerializer):
    banner_image = serializers.SerializerMethodField()
    programs = ProgramSerializer(many=True)

    class Meta:
        model = Post
        fields = [
            'slug',
            'lang',
            'url',
            'title',
            'subtitle',
            'release_date',
            'programs',
            'banner_image',
        ]

    def get_banner_image(self, obj):
        if obj.banner:
            return ImageMiniSerializer(obj.banner).data
        return None


class PostSerializer(ArchiveSerializerMixin, serializers.ModelSerializer):
    banner_image = serializers.SerializerMethodField()
    programs = ProgramSerializer(many=True)

    class Meta:
        model = Post
        fields = [
            'slug',
            'lang',
            'url',
            'title',
            'subtitle',
            'lede',
            'body',
            'links',
            'release_date',
            'programs',
            'banner_image',
        ]

    def get_banner_image(self, obj):
        if obj.banner:
            return ImageMiniSerializer(obj.banner).data
        return None
