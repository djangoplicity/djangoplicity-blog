from django.urls import path, include
from rest_framework import routers
from djangoplicity.blog.api.v2.views import PostListView, PostDetailView

api_router = routers.DefaultRouter()
api_router.register('', PostListView)
api_router.register('', PostDetailView)

urlpatterns = [
    path('', include(api_router.urls))
]
