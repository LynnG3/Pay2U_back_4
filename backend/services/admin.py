from django.contrib import admin

from .models import Category, Service



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """ Администрирование тегов. """

    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


class CatInline(admin.TabularInline):
    """Администрирование тегов к рецептам. """

    model = Service.category.through


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """ Администрирование сервисов. """

    inlines = (CatInline)
    list_display = (
        # 'name',
        # 'text',
        # 'author',
        # 'pub_date',
        # 'cooking_time',
        # 'display_ingredients',
        # 'favorite_count',
        # 'display_tags'
    )
    # search_fields = ('name', 'author__username', 'favorite_count')
    # list_filter = ('name', 'author', 'tags')

    # @admin.display(description='Теги')
    # def display_tags(self, recipe):
    #     return recipe.tags.values_list(
    #         'name', flat=True
    #     ).order_by('name')

