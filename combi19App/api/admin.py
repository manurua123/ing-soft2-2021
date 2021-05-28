from django.contrib import admin
from .models import Supplies, Driver, Bus, Place, Route, Profile, Travel, Ticket, Comment

admin.site.register(Supplies)
admin.site.register(Driver)
admin.site.register(Bus)
admin.site.register(Place)
admin.site.register(Route)
admin.site.register(Profile)
admin.site.register(Travel)
admin.site.register(Comment)


class SuppliesInline(admin.TabularInline):
    model = Ticket.supplies.through


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = (SuppliesInline,)
    exclude = ('supplies',)
# Register your models here.
