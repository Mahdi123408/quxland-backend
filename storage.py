from storages.backends.s3 import S3Storage


class CustomS3Boto3Storage(S3Storage):
    def url(self, name):
        url = super().url(name)
        return url.split('?')[0]  # حذف پارامترهای اضافی از URL
