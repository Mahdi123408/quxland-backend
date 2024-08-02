from django.db import models
from authentication.models import CustomUser
from my_methods.creators import create_random_name, change_file_name
from my_methods.validators import validate_file_name


class Files(models.Model):
    file = models.FileField(upload_to='files')
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='files')
    alt = models.CharField(max_length=255)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.file.name}: {self.author}'

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    def save(self, *args, **kwargs):
        files = Files.objects.all()
        if files:
            for file in files:
                self.file.name = validate_file_name(self.file.name)
                if file.file.name == 'files/' + self.file.name:
                    find = False
                    i = 2
                    while not find:
                        name = change_file_name(self.file.name, create_random_name(i))
                        find = True
                        for file in files:
                            if file.file.name == 'files/' + name:
                                find = False
                        i += 1
                    self.file.name = name
                    break
        super(Files, self).save(*args, **kwargs)
