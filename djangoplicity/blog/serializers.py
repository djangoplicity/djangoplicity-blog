from django.contrib.sites.shortcuts import get_current_site
from djangoplicity.archives.contrib.serialization import SimpleSerializer
from djangoplicity.archives.utils import get_instance_archives, get_instance_archives_urls
from djangoplicity.blog.models import Post

# ==========================================
# Blog Posts
# ==========================================
class PostSerializer(SimpleSerializer):
    fields = (
        'slug',
        'title',
        'subtitle',
        'lede',
        'body',
        'links',
        'release_date',
        'visuals',
        'lang',
        'url',
    )

    def get_visuals_value(self, obj):
        if obj.banner:
            return {
                'id': obj.banner.id,
                'width': obj.banner.width,
                'height': obj.banner.height,
                'formats': get_instance_archives(obj.banner),
                'formats_url': get_instance_archives_urls(obj.banner),
                'url': f'http://{get_current_site(None)}{obj.banner.get_absolute_url()}',
                'title': obj.banner.title,
            }
        return None

    def get_url_value(self, obj):
        return f'http://{get_current_site(None)}{obj.get_absolute_url()}'


class MiniPostSerializer(SimpleSerializer):
    fields = (
        'slug',
        'title',
        'subtitle',
        'lede',
        'release_date',
        'lang',
        'main_visual',
    )

    def get_main_visual_value(self, obj):
        return obj.banner.id if obj.banner else None
