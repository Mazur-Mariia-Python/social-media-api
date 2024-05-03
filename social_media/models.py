import os
import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify


def profile_picture_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.profile_picture)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/profile_pictures/", filename)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(
        blank=True,
        null=True,
        upload_to=profile_picture_file_path,
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name_plural = "profiles"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Relationship(models.Model):
    followed_at = models.DateTimeField(auto_now_add=True)
    my_follower = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="my_follower"
    )

    class Meta:
        unique_together = ("my_follower", "following")

    def __str__(self):
        return f"{self.my_follower} follows {self.following}"


def post_picture_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.post_picture)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/post_pictures/", filename)


class Post(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post_picture = models.ImageField(
        blank=True,
        null=True,
        upload_to=post_picture_file_path,
    )
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.author} at {self.created_at}"


class Comment(models.Model):
    content = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    class Meta:
        ordering = ["-commented_at"]

    def __str__(self):
        return f"Comment by {self.author} at {self.commented_at}"


class Like(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("profile", "post")
        ordering = ["-liked_at"]

    def __str__(self):
        return f"Like by {self.profile} at {self.liked_at}"
