from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Only resize if image exists and it's not the default
        if self.image and hasattr(self.image, 'path') and os.path.exists(self.image.path):
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)


class Article(models.Model):
    CATEGORY_CHOICES = [
        ("technology", "Technology"),
        ("economy", "Economy"),
        ("sports", "Sports"),
        ("politics", "Politics"),
        ("lifestyle", "Lifestyle"),
        ("entertainment", "Entertainment"),
    ]
    
    title = models.CharField(max_length=200)
    image = models.URLField(null=True, blank=True)
    url = models.TextField()
    source = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    published_at = models.DateTimeField(null=True, blank=True, help_text="Article publication date from source")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['source']),
            models.Index(fields=['-published_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.category})"


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.user.username} on {self.article.title[:50]}'