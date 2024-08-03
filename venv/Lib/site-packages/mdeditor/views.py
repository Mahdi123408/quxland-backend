from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
import os
import datetime


class UploadView(generic.View):
    """ upload image file """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        upload_image = request.FILES.get("editormd-image-file", None)

        # image none check
        if not upload_image:
            return JsonResponse({
                'success': 0,
                'message': "未获取到要上传的图片",
                'url': ""
            })

        # image format check
        file_extension = upload_image.name.split('.')[-1]
        if file_extension not in settings.MDEDITOR_CONFIGS['default']['upload_image_formats']:
            return JsonResponse({
                'success': 0,
                'message': "上传图片格式错误，允许上传图片格式为：%s" % ','.join(
                    settings.MDEDITOR_CONFIGS['default']['upload_image_formats']),
                'url': ""
            })

        # Construct the file name with timestamp
        file_full_name = '{0:%Y%m%d%H%M%S%f}.{1}'.format(datetime.datetime.now(), file_extension)

        try:
            file_path = default_storage.save(file_full_name, upload_image)
            file_url = default_storage.url(file_path)
            return JsonResponse({'success': 1,
                                 'message': "上传成功！",
                                 'url': file_url})
        except Exception as err:
            return JsonResponse({
                'success': 0,
                'message': "上传失败：%s" % str(err),
                'url': ""
            })
