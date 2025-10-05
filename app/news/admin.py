from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Article, Comment, Profile


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'category', 'created_at')
    list_filter = ('category', 'source', 'created_at')
    search_fields = ('title', 'source')
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'url', 'image', 'category', 'source')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article_title', 'rating', 'created_at', 'content_preview')
    list_filter = ('rating', 'created_at', 'article__category')
    search_fields = ('user__username', 'article__title', 'content')
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    def article_title(self, obj):
        return obj.article.title[:50] + ('...' if len(obj.article.title) > 50 else '')
    article_title.short_description = 'Article'
    
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content Preview'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'article')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Customize admin site
admin.site.site_header = 'AI News Hub Administration'
admin.site.site_title = 'AI News Hub Admin'
admin.site.index_title = 'Welcome to AI News Hub Administration'