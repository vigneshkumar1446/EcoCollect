from rest_framework import serializers
from datetime import date
import re
from api.models import User,WasteCategory,PickupRequest,Reward,RecyclerAssignment,Rating,Chatroom,Chatbox,Notification


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=['id','username','role','phone','profile_image']


class WasteCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model=WasteCategory
        fields='__all__'


class PickupRequestSerializer(serializers.ModelSerializer):


    recycler_name=serializers.SerializerMethodField()
    recycler_id=serializers.SerializerMethodField()
    is_rated=serializers.SerializerMethodField()
    # chatroom_id = serializers.SerializerMethodField()
    # unread_count = serializers.SerializerMethodField()
    # assignment_id = serializers.SerializerMethodField()

    class Meta:
        model=PickupRequest
        fields='__all__'
        read_only_fields = ['user', 'status', 'created_at']

    

    def get_recycler_name(self, obj):
        assignment = obj.recyclerassignment_set.first()
        if assignment:
            return assignment.recycler.username
        return None
    

    def get_recycler_id(self, obj):
        assignment = obj.recyclerassignment_set.first()
        if assignment:
            return assignment.recycler.id
        return None

    def get_is_rated(self, obj):
        return Rating.objects.filter(pickup=obj).exists()
    
    # def get_chatroom_id(self, obj):
    #     room = Chatroom.objects.filter(pickup=obj).first()
    #     if room:
    #         return room.id
    #     return None
    
    # def get_unread_count(self, obj):
    #     request = self.context.get("request")
    #     room = Chatroom.objects.filter(pickup=obj).first()

    #     if not room or not request:
    #         return 0

    #     return Chatbox.objects.filter(room=room, is_read=False).exclude(sender=request.user).count()
    # def get_assignment_id(self, obj):

    #     assignment = obj.recyclerassignment_set.first()

    #     if assignment:
    #         return assignment.id

    #     return None
    
    #validation 
    def validate_pickup_Date(self, value):

        if value < date.today():
            raise serializers.ValidationError(
                "Pickup date cannot be in the past."
            )

        return value
    def validate_weight(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "Weight must be greater than 0"
            )

        return value
    
    def validate(self, data):

        user = self.context["request"].user

        already_exists = PickupRequest.objects.filter(
            user=user,
            address=data["address"],
            pickup_Date=data["pickup_Date"],
            status="pending"
        ).exists()

        if already_exists:
            raise serializers.ValidationError(
                "You already created a pickup request for this address and date."
            )

        return data
    
    def validate_image(self, value):

        if value:
            if not value.content_type.startswith("image"):
                raise serializers.ValidationError(
                    "Only image files are allowed"
                )

        return value
    
    def validate_address(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Address cannot be empty"
            )

        return value

class RewardSerializer(serializers.ModelSerializer):

    class Meta:
        model=Reward
        fields='__all__'


class RecyclerAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model=RecyclerAssignment
        fields='__all__'

class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=['username','email','password','phone']
        extra_kwargs={'password':{'write_only':True}}


    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

    def validate_password(self, value):

        if len(value) < 6:
            raise serializers.ValidationError(
                "Password must be at least 6 characters"
            )

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain one uppercase letter"
            )

        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError(
                "Password must contain one number"
            )

        return value
    
    def validate_phone(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits"
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must be 10 digits"
            )

        return value

class RatingSerializers(serializers.ModelSerializer):

    class Meta:
        model=Rating
        fields='__all__'
        read_only_fields = ['user']

    def validate(self, data):
        pickup = data['pickup']
        request = self.context.get("request")
       

        if pickup.status != 'completed':
            raise serializers.ValidationError("Cannot rate before completion")

        if Rating.objects.filter(pickup=pickup).exists():
            raise serializers.ValidationError("Already rated")
        
    
        if pickup.user !=request.user:
            raise serializers.ValidationError("You are not allowed to rate this pickup")

        return data
    

class ChatboxSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Chatbox
        fields = ['id', 'room', 'sender', 'sender_name', 'image','message', 'is_read', 'created_at']
        read_only_fields = ['sender','created_at']

class ChatroomSerializer(serializers.ModelSerializer):
    
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_person = serializers.SerializerMethodField()

    class Meta:
        model = Chatroom
        fields = ["id", "pickup", "created_at", "last_message", "unread_count", "other_person"]

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-id").first()
        if msg:
            return {
                "text": msg.message if msg.message else "📷 Image",
                "time": msg.created_at
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()

    def get_other_person(self, obj):
        request = self.context.get("request")
        if not request:
            return ""

        if request.user.role == "user":
            assignment = RecyclerAssignment.objects.filter(pickup=obj.pickup).first()
            if assignment:
                return assignment.recycler.username
            return "Recycler"

        return obj.pickup.user.username
    


        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"