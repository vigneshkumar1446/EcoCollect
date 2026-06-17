from django.contrib import admin

# Register your models here.
from .models import User,WasteCategory,PickupRequest,RecyclerAssignment,Reward


admin.site.register(User)
admin.site.register(WasteCategory)
admin.site.register(PickupRequest)
admin.site.register(RecyclerAssignment)
admin.site.register(Reward)
