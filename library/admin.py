from django.contrib import admin
from django.contrib.messages import WARNING
from django.utils.html import mark_safe
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from . import models


@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ("title", "author", "status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions += ("my_action", )

    def my_action(self, request, queryset):
        book_ids = queryset.values_list("id", flat=True)
        csrf_token = get_token(request)
        message = "The following books will be updated:<br>"
        message += "".join([f"<i>{book.title}</i> by {book.author}<br>" for book in queryset])
        message += f"""
        <form action="bulk-update-status/" method="POST">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
            <input type="hidden" name="ids" value="{",".join([str(book_id) for book_id in book_ids])}">
            <h2>What status would you like to give these books?</h2>
            <select name="status">
                <option value="available">Available</option>
                <option value="on_loan">On Loan</option>
                <option value="lost">Lost</option>
            </select>
            <input type="submit" name="update_status" value="Update">
        </form>
        """
        self.message_user(request, mark_safe(message), level=WARNING)
    my_action.short_description = "Update book status"

    def bulk_update_status(self, request):
        if request.method == "POST" and "update_status" in request.POST:
            data = request.POST
            ids = [int(book_id) for book_id in data["ids"].split(",")]
            status = models.StatusChoices[data["status"]]
            queryset = models.Book.objects.filter(pk__in=ids)
            queryset.update(status=status.value)
            message = "The books were successfully updated!"
            self.message_user(request, message)
        return HttpResponseRedirect(redirect_to=reverse("admin:library_book_changelist"))

    def get_urls(self):
        urls = super().get_urls()
        additional_urls = [
            path('bulk-update-status/', self.admin_site.admin_view(self.bulk_update_status), name="bulk_update_status"),
        ]
        return additional_urls + urls


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    pass
