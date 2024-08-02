from django.http import HttpRequest
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from my_methods.validators import check_task
from my_methods.auth import check_login
from task.models import Task, CompletedTask, DailyCompletedTask
from task.serializers import TaskSerializer
from authentication.models import Referral, News, History
from authentication.serializers import ReferralViewSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.settings import CUSTOM_ACCESS_TOKEN_NAME, COUNT_CLAIM_DALY_POINTS


class TaskAndReferralListAPIView(APIView):

    @swagger_auto_schema(
        operation_description="دریافت لیستی از تسک‌ها و رفرال ها برای کاربر احراز هویت شده.",
        manual_parameters=[
            openapi.Parameter(
                CUSTOM_ACCESS_TOKEN_NAME,
                openapi.IN_HEADER,
                description="توکن احراز هویت کاربر",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="لیستی از تسک‌ها و ارجاعات",
                examples={
                    "application/json": {
                        "tasks": [
                            {
                                "id": 1,
                                "title": "db",
                                "description": "z",
                                "created_at": "2024-06-12T03:37:20.227842+03:30",
                                "updated_at": "2024-06-12T03:37:20.227842+03:30",
                                "expires_at": "2024-06-15T03:37:05+03:30",
                                "point_value": 0,
                                "image_url": "/templates/tasks/shahrdar.jpg",
                                "is_done": True,
                                "link": "http://i.com",
                                "is_active": True,
                                "expired": False
                            }
                        ],
                        "referrals": [
                            {
                                "username": "mahdi_abbasi_from_api2",
                                "full_name": "مهدی عباسی",
                                "avatar_url": None,
                                "created_at": "2024-06-14T10:38:13.566390+03:30"
                            }
                        ],
                        "daily": {
                            "can_claim": True,
                            "can_claim_after": "00:00:00",
                            "day": "1",
                            "point": "1",
                            "end": False
                        },
                        "point": 6,
                        "diamond": 0
                    }
                }
            ),
            204: "مشکلی در دریافت و پردازش اطلاعات به وجود آمده",
            404: "هیچ تسک و تسک روزانه و رفرالی پیدا نشد",
            400: openapi.Response(
                description="مشکلی در احراز هویت و اکسس توکن کاربر\nاگه Access Token Required اومد اطلاعات درست ارسال نشده\nاگه Invalid token اومد توکن اشتباهه\nاگه Token expired اومد توکن منقضی شده . ",
                examples={
                    "application/json": "Access Token Required"
                }
            ),
        },
    )
    def get(self, request: HttpRequest):
        user = check_login(request)
        if user[0]:
            user = user[1]
        elif user[1] == 'Invalid token':
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Token expired':
            return Response("Token expired", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Access Token Required':
            return Response("Access Token Required", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        try:
            tasks = Task.objects.all()
            tasks = check_task(tasks)
            referrals = Referral.objects.filter(is_active=True, from_user=user)
            # دلیل اینکه محدود نکردم به اکتیو بودن و اکسپایر نبودن
            # اینه که ممکنه کاربر یه تسک اکسپایر شده یا دی اکتیو شده رو کامل کرده باشه
            # و در تسک های کامل شدش باشه بنابراین باید همه رو بفرستم
            # و فرانت جداشون کنه و اونایی رو که برای کاربر هستن رو نشونش بده
            # حتی اگه اکسپایر و یا دی اکتیو شده و مدیریت نمایش تسک هایی که برای کاربر نیستن
            # و دی اکتیو یا اکسپایر هستن رو فرانت انجام میده و نباید نشونشون بده
        except Exception or TypeError:
            return Response(status=status.HTTP_204_NO_CONTENT)
        task_serializer = TaskSerializer(tasks, user=user, many=True)
        referral_serializer = ReferralViewSerializer(referrals, many=True)
        daily = DailyCompletedTask.objects.filter(user_id=user.id).first()
        if daily:
            now = timezone.now() + timezone.timedelta(hours=3, minutes=30)
            expt = daily.last_claimed_at + timezone.timedelta(days=1, hours=3, minutes=30)
            if str(daily.count + 1) in COUNT_CLAIM_DALY_POINTS:
                if expt < now:
                    daily_data = {
                        'can_claim': True,
                        'can_claim_after': '00:00:00',
                        'day': str(daily.count + 1),
                        'point': str(COUNT_CLAIM_DALY_POINTS[f'{daily.count + 1}']),
                        'end': False,
                    }
                else:
                    time = expt - now
                    hours, minutes = divmod(time.seconds, 3600)
                    minutes, seconds = divmod(minutes, 60)
                    daily_data = {
                        'can_claim': False,
                        'can_claim_after': f'{hours}:{minutes}:{seconds}',
                        'day': str(daily.count + 1),
                        'point': str(COUNT_CLAIM_DALY_POINTS[f'{daily.count + 1}']),
                        'end': False,
                    }
            else:
                daily_data = {
                    'can_claim': False,
                    'end': True
                }
        else:
            daily_data = {
                'can_claim': True,
                'can_claim_after': '00:00:00',
                'day': '1',
                'point': f'{COUNT_CLAIM_DALY_POINTS["1"]}',
                'end': False,
            }
        data = {}
        # daily_task = DailyTask.objects.all()
        # if daily_task:
        #     daily_task = check_daily_task(daily_task)
        #     serializer = DailyTaskSerializer(daily_task, user=user, many=True)
        #     data['daily_task'] = serializer.data
        if task_serializer.data:
            data['tasks'] = task_serializer.data
        if referral_serializer.data:
            data['referrals'] = referral_serializer.data
        data['daily'] = daily_data
        data['point'] = user.points
        data['diamond'] = user.diamond
        if data:
            return Response(data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CompleteTaskAPIView(APIView):

    @swagger_auto_schema(
        operation_description="کامل کردن تسک با آیدی .",
        manual_parameters=[
            openapi.Parameter(
                CUSTOM_ACCESS_TOKEN_NAME,
                openapi.IN_HEADER,
                description="توکن احراز هویت کاربر",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            204: "مشکلی در دریافت و پردازش اطلاعات به وجود آمده",
            400: openapi.Response(
                description="مشکلی در احراز هویت و اکسس توکن کاربر\nاگه Access Token Required اومد اطلاعات درست ارسال نشده\nاگه Invalid token اومد توکن اشتباهه\nاگه Token expired اومد توکن منقضی شده\n اگه Task already completed اومد یعنی این تسک قبلا برای یوزری که اکسس توکنش در هدره کامل شده ",
                examples={
                    "application/json": "Access Token Required"
                }
            ),
            201:
                openapi.Response(
                    description="یعنی برای بار اول درخواست زده شده و باید یک دفعه دیگه درخواست بزنه ."
                ),
            202:
                openapi.Response(
                    description="یعنی تسک با موفقیت تایید شد"
                ),
            404:
                openapi.Response(
                    description="تسک پیدا نشد"
                )
        },
    )
    def post(self, request: HttpRequest, **kwargs):
        user = check_login(request)
        if user[0]:
            user = user[1]
        elif user[1] == 'Invalid token':
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Token expired':
            return Response("Token expired", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Access Token Required':
            return Response("Access Token Required", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        try:
            if 'id' in kwargs:
                task = Task.objects.filter(id=kwargs['id'], is_active=True, expired=False).first()
                if task:
                    check_complete = CompletedTask.objects.filter(user=user, task=task).first()
                    if check_complete:
                        if check_complete.count >= 2:
                            return Response("Task already completed", status=status.HTTP_400_BAD_REQUEST)
                        else:
                            check_complete.count += 1
                            user_points = user.points
                            user.points += check_complete.task.point_value
                            check_complete.save()
                            user.save()
                            description = f'کاربر با کامل کردن تسک {task.title} {task.point_value} پوینت را گرفت و پوینت هاش از {user_points} به {user.points} افزایش پیدا کرد .'
                            News.objects.create(
                                text=description,
                            )
                            History.objects.create(
                                user=user,
                                title=f'کامل کردن تسک {task.title}',
                                description=description,
                                location='Task',
                                type='complete'
                            )
                            return Response(status=status.HTTP_202_ACCEPTED)
                    else:
                        CompletedTask.objects.create(user=user, task=task)
                        return Response(status=status.HTTP_201_CREATED)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception or TypeError:
            return Response(status=status.HTTP_204_NO_CONTENT)

    # class DailyTaskAPIView(APIView):
    #
    #     @swagger_auto_schema(
    #         operation_description="گرفتن تسک های دیلی .",
    #         manual_parameters=[
    #             openapi.Parameter(
    #                 'Authorization',
    #                 openapi.IN_HEADER,
    #                 description="توکن احراز هویت مدیر",
    #                 type=openapi.TYPE_STRING,
    #                 required=True
    #             ),
    #             openapi.Parameter(
    #                 CUSTOM_ACCESS_TOKEN_NAME,
    #                 openapi.IN_HEADER,
    #                 description="توکن احراز هویت کاربر",
    #                 type=openapi.TYPE_STRING,
    #                 required=True
    #             ),
    #         ],
    #         responses={
    #             400: openapi.Response(
    #                 description="مشکلی در احراز هویت و اکسس توکن کاربر\nاگه Access Token Required اومد اطلاعات درست ارسال نشده\nاگه Invalid token اومد توکن اشتباهه\nاگه Token expired اومد توکن منقضی شده",
    #                 examples={
    #                     "application/json": "Access Token Required"
    #                 }
    #             ),
    #             200:
    #                 openapi.Response(
    #                     description="با موفقیت اطلاعات برگشت .",
    #                     examples={"application/json": [
    #                         {
    #                             "id": 1,
    #                             "last_submit": "2024-06-12T05:09:17.326232Z",
    #                             "can_submit": True,
    #                             "can_submit_time": "2024-06-13T05:09:17.326232Z",
    #                             "title": "شروع دوره های تابستانی",
    #                             "description": "uiyutgfdvsdc",
    #                             "created_at": "2024-06-12T04:05:50.284404+03:30",
    #                             "updated_at": "2024-06-12T04:05:50.284404+03:30",
    #                             "expires_at": "2024-06-16T04:05:41+03:30",
    #                             "expired": False,
    #                             "point_value": 0,
    #                             "image_url": "/templates/tasks/daily/shahrdar.jpg",
    #                             "is_active": True
    #                         },
    #                         {
    #                             "id": 2,
    #                             "last_submit": "2024-06-13T09:19:58.858689Z",
    #                             "can_submit": True,
    #                             "can_submit_time": "2024-06-14T09:19:58.858689Z",
    #                             "title": "gb",
    #                             "description": "g",
    #                             "created_at": "2024-06-12T04:48:14.161780+03:30",
    #                             "updated_at": "2024-06-12T04:48:14.161780+03:30",
    #                             "expires_at": "2024-06-15T04:48:04+03:30",
    #                             "expired": False,
    #                             "point_value": 1,
    #                             "image_url": "/templates/tasks/daily/shahrdar_GLMhobO.jpg",
    #                             "is_active": True
    #                         }
    #                     ]}
    #                 ),
    #             404:
    #                 openapi.Response(
    #                     description="تسک پیدا نشد"
    #                 )
    #         },
    #     )
    #     def get(self, request: HttpRequest):
    #         user = check_login(request)
    #         if user[0]:
    #             user = user[1]
    #         elif user[1] == 'Invalid token':
    #             return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
    #         elif user[1] == 'Token expired':
    #             return Response("Token expired", status=status.HTTP_400_BAD_REQUEST)
    #         elif user[1] == 'Access Token Required':
    #             return Response("Access Token Required", status=status.HTTP_400_BAD_REQUEST)
    #         else:
    #             return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
    #         daily_task = DailyTask.objects.all()
    #         if daily_task:
    #             daily_task = check_daily_task(daily_task)
    #             serializer = DailyTaskSerializer(daily_task, user=user, many=True)
    #             return Response(serializer.data)
    #         else:
    #             return Response(status=status.HTTP_404_NOT_FOUND)


class DailyCompleteTaskAPIView(APIView):

    @swagger_auto_schema(
        operation_description="گرفتن پوینت روزانه دیلی .",
        manual_parameters=[
            openapi.Parameter(
                CUSTOM_ACCESS_TOKEN_NAME,
                openapi.IN_HEADER,
                description="توکن احراز هویت کاربر",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            400: openapi.Response(
                description="مشکلی در احراز هویت و اکسس توکن کاربر یا کامل شدن تسک\nاگه Access Token Required اومد اطلاعات درست ارسال نشده\nاگه Invalid token اومد توکن اشتباهه\nاگه Token expired اومد توکن منقضی شده\nاگه can_claim_after اومد یعنی امروز کلیم شده و بعد از تایمی که برمیگرده میشه دوباره کلیم کرد .\nاگه You have received all اومد یعنی تمام پوینت ها رو کلیم کرده و دیگه نمیتونه کلیم کنه .",
                examples={
                    "application/json": {
                        "can_claim_after": "2024-07-03T22:48:26.200192Z"
                    }
                }
            ),
            200:
                openapi.Response(
                    description="ثبت شد . "
                )
        },
    )
    def post(self, request: HttpRequest):
        user = check_login(request)
        if user[0]:
            user = user[1]
        elif user[1] == 'Invalid token':
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Token expired':
            return Response("Token expired", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Access Token Required':
            return Response("Access Token Required", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        check_daily_task_comp = DailyCompletedTask.objects.filter(user_id=user.id).first()
        if check_daily_task_comp:
            if check_daily_task_comp.count >= len(COUNT_CLAIM_DALY_POINTS):
                return Response("You have received all", status=status.HTTP_400_BAD_REQUEST)
            now = timezone.now() + timezone.timedelta(hours=3, minutes=30)
            expt = check_daily_task_comp.last_claimed_at + timezone.timedelta(days=1, hours=3, minutes=30)
            if expt < now:
                check_daily_task_comp.last_claimed_at = timezone.now()
                check_daily_task_comp.count += 1
                user_points = user.points
                user.points += COUNT_CLAIM_DALY_POINTS[f'{check_daily_task_comp.count}']
                check_daily_task_comp.save()
                description = f'کاربر با کلیم کردن تسک روزانه روز {check_daily_task_comp.count}، {COUNT_CLAIM_DALY_POINTS[f'{check_daily_task_comp.count}']} پوینت را گرفت و پوینت هاش از {user_points} به {user.points} افزایش پیدا کرد .'
                News.objects.create(
                    text=description,
                )
                History.objects.create(
                    user=user,
                    title=f'کلیم کردن تسک روزانه روز {check_daily_task_comp.count}',
                    description=description,
                    location='DailyTask',
                    type='complete'
                )
                user.save()
                return Response(status=status.HTTP_200_OK)
            else:
                time = expt - now
                hours, minutes = divmod(time.seconds, 3600)
                minutes, seconds = divmod(minutes, 60)
                data = {
                    'can_claim_after': f'{hours}:{minutes}:{seconds}',
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            DailyCompletedTask.objects.create(user=user)
            user_points = user.points
            user.points += COUNT_CLAIM_DALY_POINTS['1']
            user.save()
            description = f'کاربر با کلیم کردن تسک روزانه روز 1، {COUNT_CLAIM_DALY_POINTS["1"]} پوینت را گرفت و پوینت هاش از {user_points} به {user.points} افزایش پیدا کرد .'
            News.objects.create(
                text=description,
            )
            History.objects.create(
                user=user,
                title=f'کلیم کردن تسک روزانه روز 1',
                description=description,
                location='DailyTask',
                type='complete'
            )
            return Response(status=status.HTTP_200_OK)
