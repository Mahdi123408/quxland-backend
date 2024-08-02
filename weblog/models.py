from django.db import models
from my_methods.creators import create_random_name, change_file_name
from my_methods.validators import validate_file_name
from mdeditor.fields import MDTextField
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Article(models.Model):
    title = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='articles/')
    content = MDTextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    short_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Articles'

    def save(self, *args, **kwargs):
        files = Article.objects.all()
        if files:
            for file in files:
                self.thumbnail.name = validate_file_name(self.thumbnail.name)
                if file.thumbnail.name == 'articles/' + self.thumbnail.name:
                    find = False
                    i = 2
                    while not find:
                        name = change_file_name(self.thumbnail.name, create_random_name(i))
                        find = True
                        for file in files:
                            if file.thumbnail.name == 'articles/' + name:
                                find = False
                        i += 1
                    self.thumbnail.name = name
                    break
        super(Article, self).save(*args, **kwargs)
