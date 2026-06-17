from rest_framework.permissions import BasePermission,SAFE_METHODS

class IsRecycler(BasePermission):

    def has_permission(self, request, view):

        if request.method=='GET':
            return True
        
        if request.method=="POST":
            return request.user.role =="user"
        
        if request.method in ['PATCH','PUT']:
            return request.user.role =="recycler"
        
        return False
        
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and (
            request.user.role == "admin" or request.user.is_superuser
        )



        