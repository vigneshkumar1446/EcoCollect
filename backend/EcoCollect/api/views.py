from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes,action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .permission import IsRecycler,IsAdminOrReadOnly
from django.db.models import Avg,Max
from .models import User, WasteCategory,RecyclerAssignment,Reward,PickupRequest,Rating,Notification,Chatbox,Chatroom
from .serializers import UserSerializer, RegisterSerializer,WasteCategorySerializer,PickupRequestSerializer,RecyclerAssignmentSerializer,RatingSerializers,NotificationSerializer,ChatboxSerializer,ChatroomSerializer
# Create your views here
# 
# 
# 
# 
@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
   
@api_view(['POST'])
def register_user(request):

    serializer = RegisterSerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):

    
    user = request.user

    rewards=Reward.objects.filter(user=user)
    pickups = PickupRequest.objects.filter(user=user)

    data = {
        "total": pickups.count(),
        "pending": pickups.filter(status="pending").count(),
        "approved": pickups.filter(status="approved").count(),
        "completed": pickups.filter(status="completed").count(),

        "points": sum(r.points for r in rewards),

        "reward_history": list(
            rewards.values("points", "description", "created_at")
        ),


        "recent": list(
            pickups.order_by("-id")[:5].values(
                "id", "address", "status", "pickup_Date"
            )
        )

    }

    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recycler_rating_stats(request):
    if request.user.role != "recycler":
        return Response({"error": "Only recycler can access this"}, status=403)

    ratings = Rating.objects.filter(recycler=request.user)

    average_rating = ratings.aggregate(avg=Avg("rating"))["avg"] or 0

    data = {
        "average_rating": round(average_rating, 1),
        "total_reviews": ratings.count(),
        "recent_reviews": list(
            ratings.order_by("-created_at").values(
                "rating",
                "review",
                "created_at"
            )[:5]
        )
    }

    return Response(data)
@api_view(["PATCH"])
def mark_notifications_read(request):
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return Response({"message": "Notifications marked as read"})




class WasteCategoryViewset(ModelViewSet):
    queryset=WasteCategory.objects.all()
    serializer_class=WasteCategorySerializer
    permission_classes=[IsAdminOrReadOnly]

class PickupRequestViewset(ModelViewSet):

    queryset=PickupRequest.objects.all()
    serializer_class=PickupRequestSerializer
    permission_classes=[IsAuthenticated,IsRecycler]

    def perform_create(self, serializer):

        
        pickup = serializer.save(user=self.request.user)

        recycler = User.objects.filter(role='recycler').first()

        RecyclerAssignment.objects.create(
            pickup=pickup,
            recycler=recycler
        )
        Notification.objects.create(
            user=recycler,
            message="New pickup assigned"
        )


    
      ###  APPROVE (ONLY RECYCLER)
    @action(detail=True, methods=["patch"])
    def approve(self, request, pk=None):

        pickup = self.get_object()

        if request.user.role != "recycler":
            return Response({"error": "Not allowed"}, status=403)
        
        if pickup.status != "pending":
           return Response({"error": "Only pending pickup can be approved"}, status=400)


        pickup.status = "approved"
        pickup.save()

        # Assign recycler here
        if not RecyclerAssignment.objects.filter(pickup=pickup).exists():
            RecyclerAssignment.objects.create(
                pickup=pickup,
                recycler=request.user
            )
        Chatroom.objects.get_or_create(pickup=pickup)

        Notification.objects.create(
            user=pickup.user,
            message=f"Your pickup request #{pickup.id} was approved by {request.user.username}"
        )

        Notification.objects.create(
            user=request.user,
            message=f"You approved pickup request #{pickup.id}."
        )


        return Response({"message": "Pickup Approved"})

    
    @action(detail=True, methods=["patch"])
    def reject(self, request, pk=None):

        pickup = self.get_object()

        if request.user.role != "recycler":
            return Response({"error": "Not allowed"}, status=403)

        pickup.status = "rejected"
        pickup.save()

        create_notification(
            pickup.user,
            f"Your pickup request #{pickup.id} was rejected."
        )


        return Response({"message": "Pickup Rejected"})

    #  COMPLETE
    @action(detail=True, methods=["patch"])
    def complete(self, request, pk=None):

        pickup = self.get_object()

        if request.user.role != "recycler":
            return Response({"error": "Not allowed"}, status=403)
        if pickup.status == "completed":
            return Response(
                {"error": "Pickup already completed"},
                status=400
            )

        pickup.status = "completed"
        
        # SAVE COMPLETION IMAGE
        if "completion_image" in request.FILES:
            pickup.completion_image = request.FILES[
                "completion_image"
            ]

        # SAVE COMPLETION NOTE
        pickup.completion_note = request.data.get(
            "completion_note",
            ""
        )

        pickup.save()

        #  Reward per pickup (fix)
        # GIVE REWARD
        Reward.objects.create(
            user=pickup.user,
            points=50,
            description=f"Reward for pickup #{pickup.id}"
)
        Notification.objects.create(
            user=pickup.user,
            message="Pickup completed "
        )
        return Response({"message": "Completed + Reward given"})


    def get_queryset(self):

        user = self.request.user

        if user.is_superuser:
            queryset = PickupRequest.objects.all()

        elif user.role == "user":
            queryset = PickupRequest.objects.filter(user=user)

        elif user.role == "recycler":
            queryset = (
                PickupRequest.objects.filter(
                    recyclerassignment__recycler=user
                )
                |
                PickupRequest.objects.filter(status="pending")
            )

        else:
            queryset = PickupRequest.objects.all()

        # CATEGORY FILTER
        category = self.request.query_params.get("category")

        if category:
            queryset = queryset.filter(
                category__name__icontains=category
            )

        return queryset




class RecyclerAssignmentViewSet(ModelViewSet):

    queryset = RecyclerAssignment.objects.all()
    serializer_class = RecyclerAssignmentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["PATCH"])
    def update_location(self, request, pk=None):

        assignment = self.get_object()

        assignment.latitude = request.data.get("latitude")
        assignment.longitude = request.data.get("longitude")

        assignment.save()

        return Response({
            "message": "Location updated"
        })


class RatingViewSet(ModelViewSet):

    queryset=Rating.objects.all()
    serializer_class=RatingSerializers
    permission_classes=[IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    
#CHAT

class ChatroomViewSet(ModelViewSet):
    serializer_class = ChatroomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # room_id=self.request.query_params.get("room")


        if user.role == "user":
            qs=Chatroom.objects.filter(pickup__user=user)

        elif user.role == "recycler":
            qs=Chatroom.objects.filter(
                pickup__recyclerassignment__recycler=user
            )
        

        
        else:
            return Chatroom.objects.none()
    
        qs= qs.annotate(
            last_msg_time=Max("messages__created_at")
        ).order_by("-last_msg_time")

        return qs
    
     
    
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

class ChatboxViewSet(ModelViewSet):
    serializer_class = ChatboxSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        room_id = self.request.query_params.get("room")

        qs = Chatbox.objects.all()

        if user.role == "user":
            qs = qs.filter(room__pickup__user=user)

        elif user.role == "recycler":
            qs = qs.filter(room__pickup__recyclerassignment__recycler=user)

        else:
            qs = Chatbox.objects.none()

        if room_id:
            qs = qs.filter(room_id=room_id)

            qs.exclude(sender=user).filter(is_read=False).update(is_read=True)


        return qs.order_by("id")

    def perform_create(self, serializer):
        room = serializer.validated_data["room"]
        user = self.request.user

        allowed = False

        if room.pickup.user == user:
            allowed = True

        assignment = RecyclerAssignment.objects.filter(pickup=room.pickup, recycler=user).exists()
        if assignment:
            allowed = True

        if not allowed:
            raise serializer.ValidationError("You are not allowed to send message in this room")

        serializer.save(sender=user)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recycler_pickup_history(request):
    if request.user.role != "recycler":
        return Response({"error": "Only recycler can access this"}, status=403)

    completed_pickups = PickupRequest.objects.filter(
        recyclerassignment__recycler=request.user,
        status="completed"
    ).order_by("-id")

    data = []

    for pickup in completed_pickups:
        rating = Rating.objects.filter(pickup=pickup).first()

        data.append({
            "id": pickup.id,
            "user": pickup.user.username,
            "category": pickup.category.name,
            "weight": pickup.weight,
            "address": pickup.address,
            "pickup_date": pickup.pickup_Date,
            "status": pickup.status,
            "rating": rating.rating if rating else None,
            "review": rating.review if rating else None,
        })

    return Response(data)


#ADMIN Section

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Only admin can access this"}, status=403)

    data = {
        "total_users": User.objects.filter(role="user").count(),
        "total_recyclers": User.objects.filter(role="recycler").count(),
        "total_pickups": PickupRequest.objects.count(),
        "pending_pickups": PickupRequest.objects.filter(status="pending").count(),
        "approved_pickups": PickupRequest.objects.filter(status="approved").count(),
        "completed_pickups": PickupRequest.objects.filter(status="completed").count(),
        "total_categories": WasteCategory.objects.count(),
    }

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_manage_users(request):
    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Only admin can access this"}, status=403)

    users = User.objects.all().order_by("-id")

    data = []
    for user in users:
        data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
        })

    return Response(data)





@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_user(request, user_id):
    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Only admin can access this"}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    user.username = request.data.get("username", user.username)
    user.email = request.data.get("email", user.email)
    user.phone = request.data.get("phone", user.phone)
    user.role = request.data.get("role", user.role)

    user.save()

    return Response({
        "message": "User updated successfully",
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
    })