from modeltranslation.translator import register, TranslationOptions
from .models import Category, Author


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'footer',)


@register(Author)
class AuthorTranslationOptions(TranslationOptions):
    fields = ('biography',)
