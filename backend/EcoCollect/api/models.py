from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

#USER model


class User(AbstractUser):
    role_choice=(
        ('user','User'),
        ('admin','Admin'),
        ('recycler','Recycler')
    )

    role=models.CharField(max_length=20,choices=role_choice, default='user')
    phone=models.CharField(max_length=10, blank=True ,null=True)
    profile_image = models.ImageField(
    upload_to="profiles/",
    null=True,
    blank=True
    )
    
    def __str__(self):
        return f"{self.username}-{self.role}"


class WasteCategory(models.Model):

    name=models.CharField(max_length=70)
    description=models.TextField()
    image=models.ImageField(upload_to='categories/', blank=True, null=True)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PickupRequest(models.Model):

    status_choice=(
        ('completed','Completed'),
        ('pending','Pending'),
        ('approved','Accepted'),
        ('rejected','Rejected')
    )



    user=models.ForeignKey(User,on_delete=models.CASCADE)
    category=models.ForeignKey(WasteCategory,on_delete=models.CASCADE)
    weight=models.FloatField()
    address=models.TextField()
    pickup_Date=models.DateField()
    status=models.CharField(max_length=10,choices=status_choice,default='pending')
    created_at=models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to="pickup_images/", blank=True, null=True)
    
    latitude = models.FloatField(
    null=True,
    blank=True
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"
   


class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.points} points"


class RecyclerAssignment(models.Model):

    pickup = models.ForeignKey(PickupRequest, on_delete=models.CASCADE)
    recycler = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'recycler'})
    assigned_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.recycler.username} assigned to {self.pickup.id}"



class Rating(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE )
    recycler=models.ForeignKey(User, on_delete=models.CASCADE,  related_name="recycler_ratings")
    pickup=models.OneToOneField(PickupRequest, on_delete=models.CASCADE)

    rating=models.IntegerField()
    review=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)


class Chatroom(models.Model):
    pickup=models.OneToOneField(PickupRequest,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"Chatroom for Pickup {self.pickup.id}"


class Chatbox(models.Model):
    room=models.ForeignKey(Chatroom, on_delete=models.CASCADE, related_name="messages")
    sender=models.ForeignKey(User,on_delete=models.CASCADE)
    image = models.ImageField(upload_to="Chat/", blank=True, null=True)
    message=models.TextField()
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
 

    def __str__(self):
        return self.message
   