from djangoplicity.blog.models import Post
from djangoplicity.blog.options import BlogPostOptions
from djangoplicity.translation.api.v2.views import TranslationAPIViewMixin, DEFAULT_API_TRANSLATION_MODE
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from djangoplicity.blog.api.v2.serializers import PostMiniSerializer, PostSerializer
from rest_framework import permissions, mixins
from rest_framework.viewsets import GenericViewSet
from django_filters import rest_framework as filters


class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class PostFilter(filters.FilterSet):
    program = filters.CharFilter(field_name="programs__url")
    search = filters.CharFilter(method='search_filter')
    is_e_and_e = filters.BooleanFilter(field_name="is_e_and_e")

    class Meta:
        model = Post
        fields = ['program', 'is_e_and_e']

    def search_filter(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(subtitle__icontains=value) |
                Q(lede__icontains=value) |
                Q(body__icontains=value)
            )
        return queryset


class PostViewMixin:
    def get_queryset(self):
        is_e_and_e = self.request.GET.get('is_e_and_e', 'false').lower()
        
        if is_e_and_e == 'true':
            qs, _ = BlogPostOptions.Queries.e_and_e.queryset(
                Post, BlogPostOptions, self.request,
                mode=self.request.GET.get('translation_mode', DEFAULT_API_TRANSLATION_MODE)
            )
        else:
            qs, _ = BlogPostOptions.Queries.default.queryset(
                Post, BlogPostOptions, self.request,
                mode=self.request.GET.get('translation_mode', DEFAULT_API_TRANSLATION_MODE)
            )
        
        return qs


@extend_schema(
    parameters=[
        OpenApiParameter(
            "program",
            OpenApiTypes.STR,
            description="The program identifier, e.g: kpno, rubin, gemini, ctio, csdc, noao, useltp, noirlab"
        ),
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            description="Search by title, subtitle, lede, or body"
        ),
        OpenApiParameter(
            "is_e_and_e",
            OpenApiTypes.BOOL,
            description="If you select ‘true’, you will receive the E&E category posts.",
            default=False 
        ),
        OpenApiParameter(
            "page_size",
            OpenApiTypes.INT,
            description=f"Number of results to return per page. Max: {PostPagination.max_page_size}, Default: {PostPagination.page_size}"
        ),
    ],
)
class PostListView(mixins.ListModelMixin, PostViewMixin, TranslationAPIViewMixin, GenericViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Post.objects.none()
    serializer_class = PostMiniSerializer
    pagination_class = PostPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PostFilter


class PostDetailView(mixins.RetrieveModelMixin, PostViewMixin, TranslationAPIViewMixin, GenericViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Post.objects.none()
    serializer_class = PostSerializer