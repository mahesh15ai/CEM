from django.contrib import admin
from .models import StudentProfile, BannerImage, AnnouncementNotice

admin.site.register(StudentProfile)

@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge_text', 'is_active', 'created_at')
    list_filter = ('is_active',)

@admin.register(AnnouncementNotice)
class AnnouncementNoticeAdmin(admin.ModelAdmin):
    list_display = ('notice_text', 'is_active', 'created_at')
    list_filter = ('is_active',)