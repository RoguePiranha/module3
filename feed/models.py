from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Post(models.Model):
    description = (
        models.TextField(
            max_length=500,
            help_text="Enter a description of your post",
            verbose_name="Description",
            blank=True,
        ),
    )
    pic = (
        models.ImageField(
            upload_to="path/to/img", blank=True, null=True, verbose_name="Post Image"
        ),
    )
    date_posted = (
        models.DateTimeField(default=timezone.now, verbose_name="Date Posted"),
    )
    user_name = (
        models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User Name"),
    )
    tags = (models.ManyToManyField("Tag", blank=True, verbose_name="Tags"),)

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})


class Comments(models.Model):
    comment = (
        models.TextField(
            max_length=500, help_text="Enter a comment", verbose_name="Comment"
        ),
    )
    date_posted = (
        models.DateTimeField(default=timezone.now, verbose_name="Date Posted"),
    )
    user_name = (
        models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User Name"),
    )
    post = (models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="Post"),)


class Likes(models.Model):
    user_name = (
        models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User Name"),
    )
    post = (models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="Post"),)
