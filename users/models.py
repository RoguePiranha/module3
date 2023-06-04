from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save

# Create your models here.


class Profile(models.Model):
    username = models.OneToOneField(
        User,
        max_length=100,
        help_text="Enter your desired username (this will be your display name, or you can use your first and last name by leaving this field blank)",
        blank=True,
        verbose_name="Username",
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(
        max_length=100, help_text="Enter your first name", verbose_name="First Name"
    )
    last_name = models.CharField(
        max_length=100, help_text="Enter your last name", verbose_name="Last Name"
    )
    image = models.ImageField(
        upload_to="profile_pics", blank=True, null=True, verbose_name="Profile Picture"
    )
    email = models.EmailField(
        max_length=100,
        help_text="Enter your email address",
        verbose_name="Email Address",
    )
    bio = models.TextField(
        max_length=500, help_text="Enter a short bio about yourself", verbose_name="Bio"
    )
    friends = models.ManyToManyField(
        "self", blank=True, verbose_name="Friends", symmetrical=False
    )
    slug = AutoSlugField(populate_from="username", unique=True, null=True)

    # set the default ordering for the model
    class Meta:
        ordering = ["username", "first_name", "last_name"]

    # defines the username as the user's first name + last name if no username is provided
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.first_name + self.last_name
        self.username = self.username.lower()
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("profile-detail", kwargs={"slug": self.slug})


def post_save_user_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        try:
            Profile.objects.create(user=instance)
        except:
            pass


post_save.connect(post_save_user_model_receiver, sender=settings.AUTH_USER_MODEL)


class FriendRequest(models.Model):
    to_user = models.ForeignKey(
        Profile, related_name="to_user", on_delete=models.CASCADE
    )
    from_user = models.ForeignKey(
        Profile, related_name="from_user", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.from_user} to {self.to_user}"
