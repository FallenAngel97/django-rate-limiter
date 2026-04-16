from django.contrib import admin
from .models import ApiLimiter, UserSpecificLimit
from django_redis import get_redis_connection
import logging
import hashlib

redis = get_redis_connection("default")

DEFAULT_REDIS_KEY_FOR_UNMAPPED_USERS = "default"


class UserSpecificLimitInline(admin.TabularInline):
    model = UserSpecificLimit

@admin.register(ApiLimiter)
class ApiLimiterAdmin(admin.ModelAdmin):
    inlines = [
        UserSpecificLimitInline
    ]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        for formset in formsets:
            for form_instance in formset.forms:
                if form_instance.cleaned_data:
                    parent_obj = form_instance.cleaned_data.get("api_limiter")
                    affected_user = form_instance.cleaned_data.get("affected_user")
                    speed_value = form_instance.cleaned_data.get("speed_value")
                    user_tokens = affected_user.oauth2_provider_accesstoken.all()
                    md5_url = hashlib.md5(parent_obj.url.encode('utf-8')).hexdigest()

                    redis_key = f"api_limit:{parent_obj.method}:{md5_url}"
                    for token in user_tokens:
                        logging.debug(f"Saving to redis key {redis_key} with subfield {token.token}, value {speed_value}")
                        redis.hset(redis_key, token.token, speed_value)


    def save_model(self, request, obj, form, change):
        changed_fields = form.changed_data

        old_values = {
            field: form.initial.get(field)
            for field in changed_fields
        }

        new_values = {
            field: form.cleaned_data.get(field)
            for field in changed_fields
        }

        super().save_model(request, obj, form, change)

        # due to the fact that the URL stored in the Redis in key, we are getting 
        # either the old URL (in case URL has changed) or the one stored in DB
        url_affected = old_values.get('url') or obj.url
        md5_url = hashlib.md5(url_affected.encode('utf-8')).hexdigest()
        rate = new_values.get('speed_value', obj.speed_value)

        redis_key = f"api_limit:{obj.method}:{md5_url}"
        
        # Push diff to Redis
        redis.hset(redis_key, DEFAULT_REDIS_KEY_FOR_UNMAPPED_USERS, rate)
