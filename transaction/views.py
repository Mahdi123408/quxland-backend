from django.http import HttpRequest
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from my_methods.validators import check_task
from my_methods.auth import check_login
from my_methods.validators import validate_user_wallet, get_transaction_by_address, find_transaction, get_bnb_price
from my_methods.creators import convert_timestamp
from transaction.models import *
from transaction.serializers import *
from authentication.models import Referral, News, History
from authentication.serializers import ReferralViewSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.settings import CUSTOM_ACCESS_TOKEN_NAME, COUNT_CLAIM_DALY_POINTS, TIME_DIFFERENCE_WITH_BNB, WALLET


class DiamondPackageListAPIView(APIView):
    @swagger_auto_schema(
        operation_description="دریافت لیستی از دایموند پکیج های قابل خرید .",
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
                description="لیستی از دایموند پکیج های قابل خرید .",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "title": "شروع دوره های تابستانی",
                            "thumbnail": "https://iranverse.storage.c2.liara.space/iranverse/images/diamond_thumbnail/5_TwG0EWU.png",
                            "description": "dvgfhj,k",
                            "short_description": "srhfrgdh",
                            "value": 2,
                            "price": 22.1,
                            "type": "d",
                            "discount": 2.1,
                            "is_active": True,
                            "created_at": "2024-07-25T22:08:57",
                            "updated_at": "2024-07-26T15:30:42",
                            "price_bnb": 0.038275043812300825,
                            "discount_bnb": 0.0036369951133860515
                        }
                    ]
                }
            ),
            404: "هیچ دایموند پکیج قابل خریدی پیدا نشد",
            400: openapi.Response(
                description="مشکلی در احراز هویت و اکسس توکن کاربر\nاگه Access Token Required اومد اطلاعات درست ارسال نشده\nاگه Invalid token اومد توکن اشتباهه\nاگه Token expired اومد توکن منقضی شده . ",
                examples={
                    "application/json": "Access Token Required"
                }
            ),
        },
    )
    def get(self, request):
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
        diamond = DiamondPackage.objects.filter(is_active=True)
        if not diamond:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DiamondSerializer(diamond, many=True)
        data = serializer.data
        b = 0
        bnb_price = get_bnb_price()
        while b < len(data):
            data[b]['created_at'] = data[b]['created_at'][:19]
            data[b]['updated_at'] = data[b]['updated_at'][:19]
            data[b]['price'] += 5
            data[b]['price_bnb'] = data[b]['price'] / bnb_price
            data[b]['discount_bnb'] = data[b]['discount'] / bnb_price
            b += 1
        return Response(serializer.data)


class BuyDiamondPackageAPIView(APIView):
    @swagger_auto_schema(
        operation_description="ثبت خرید دایموند .",
        manual_parameters=[
            openapi.Parameter(
                CUSTOM_ACCESS_TOKEN_NAME,
                openapi.IN_HEADER,
                description="توکن احراز هویت کاربر",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'tx_hash': openapi.Schema(type=openapi.TYPE_STRING, description='هش تراکنش',
                                          ),

            },
            required=['tx_hash']
        ),
        responses={
            400: openapi.Response(
                description="مشکلی در احراز هویت و اکسس توکن کاربر یا ثبت خرید\nاگه Access Token Required اومد اطلاعات درست ارسال نشده\nاگه Invalid token اومد توکن اشتباهه\nاگه Token expired اومد توکن منقضی شده\nاگه Invalid wallet اومد یعنی یا ولت نداره یا ولتش اشتباهه\nاگه 'error': 'amount and tx_hash are required .' اومد یعنی مقادیر درست ارسال نشدن\nاگه 'error': 'fake transaction and take strike' اومد یعنی تلاش غیر قانونی و اشتباه برای ثبت تراکنش اتفاق افتاده و کاربر یک استرایک گرفته\nاگه 'error': 'error in transaction' اومد یعنی مشکلی در تراکنش کاربر وجود داشته ولی استرایک نمیخوره\nاگه 'error': 'error in verifying the transaction' اومد یعنی یه خطایی در پردازش به وجود اومده که پیشبینی نشده بود و باید به پشتیبانی پیام بده و هیستوری تراکنشش هم ثبت شده .\nاگه 'error': 'not enough money' اومد یعنی مقدار کمی توکن زده .\nاگه 'error': 'transaction is repeated' اومد یعنی که تراکنش تتکراری است .",
                examples={
                    "application/json": "Access Token Required"
                }
            ),
            404: openapi.Response(
                description="پیدا نشدن پک"
            ),
            200: openapi.Response(
                description="اطلاعات تراکنش درست بوده",
                examples={
                    "application/json": {
                        "time": "2024-07-26 16:07:55",
                        "from_address": "0x6855f64b108ff06138018ddff01008d2548a3fe6",
                        "to_address": "0x3a3983e4bd7bcbeb0e67c39eb0c0957f6aa05feb",
                        "amount_transaction": 0.044,
                        "bnb_price": 577.073587825935,
                        "diamond_value": 2
                    }
                }
            ),
        },
    )
    def post(self, request, diamond_id):
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
        check_wallet = validate_user_wallet(user.wallet_address)
        if not check_wallet:
            return Response("Invalid wallet", status=status.HTTP_400_BAD_REQUEST)
        diamond = DiamondPackage.objects.filter(id=diamond_id, is_active=True).first()
        if not diamond:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if 'tx_hash' not in request.data:
            return Response(data={
                'error': 'tx_hash are required .'
            }, status=status.HTTP_400_BAD_REQUEST)
        tx_hash = request.data['tx_hash']
        hash_check = get_transaction_by_address(user.wallet_address)
        if not hash_check or hash_check[0]['status'] == '0' and hash_check[0]['message'] == 'No transactions found' or \
                hash_check[1]['status'] == '0' and hash_check[1]['message'] == 'No transactions found':
            user.strike += 1
            user.save()
            now = timezone.now()
            History.objects.create(user=user, title='اضافه شدن یک اخطار به دلیل تلاش برای ثبت تراکنش جعلی',
                                   description=f'کاربر در تاریخ {now} با تلاش برای ثبت تراکنش جعلی برای خرید پکیج {diamond.title} یک استرایک خورد .',
                                   location='Transaction', type='strike')
            return Response(data={
                'error': 'fake transaction and take strike',
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            transaction_check = Transaction.objects.filter(tx_hash=tx_hash).first()
            if transaction_check:
                now = timezone.now()
                History.objects.create(user=user, title='خرید ناموفق به دلیل تکراری بودن تراکنش',
                                       description=f'کاربر در تاریخ {now} با تلاش برای ثبت تراکنش برای خرید پکیج {diamond.title} به مشکل تکراری بودن تراکنش بر خورد .\nهش تراکنش : {tx_hash} \n پکیج : {diamond}',
                                       location='Transaction', type='buy')
                return Response(data={
                    'error': 'transaction is repeated',
                }, status=status.HTTP_400_BAD_REQUEST)
            transaction_my_wallet = find_transaction(tx_hash, hash_check[0]['result'])
            transaction_user_wallet = find_transaction(tx_hash, hash_check[1]['result'])
            if transaction_my_wallet and transaction_user_wallet:
                if transaction_my_wallet['isError'] == '1' or transaction_user_wallet['isError'] == '1':
                    now = timezone.now()
                    Transaction.objects.create(tx_hash=tx_hash, user=user, amount=transaction_my_wallet['value'],
                                               status=0, for_buy=diamond)
                    History.objects.create(user=user, title='خرید ناموفق به دلیل اشکال در تراکنش',
                                           description=f'کاربر در تاریخ {now} با تلاش برای ثبت تراکنش برای خرید پکیج {diamond.title} به مشکلی در تراکنش خورد .\nهش تراکنش : {tx_hash} \n پکیج : {diamond}',
                                           location='Transaction', type='buy')
                    return Response(data={
                        'error': 'error in transaction',
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.strike += 1
                user.save()
                now = timezone.now()
                History.objects.create(user=user, title='اضافه شدن یک اخطار به دلیل تلاش برای ثبت تراکنش جعلی',
                                       description=f'کاربر در تاریخ {now} با تلاش برای ثبت تراکنش جعلی برای خرید پکیج {diamond.title} یک استرایک خورد به این دلیل که هش ارسال شده یا در تراکنش های ولت ما نبوده یا در تراکنش های ولت کاربر .\nهش تراکنش : {tx_hash}',
                                       location='Transaction', type='strike')
                return Response(data={
                    'error': 'fake transaction and take strike',
                }, status=status.HTTP_400_BAD_REQUEST)

            time_send = convert_timestamp(transaction_my_wallet['timeStamp']) + TIME_DIFFERENCE_WITH_BNB
            from_address = transaction_user_wallet['from']
            to_address = transaction_user_wallet['to']

            amount_transaction = int(transaction_user_wallet['value']) / 1000000000000000000
            if from_address.lower() != user.wallet_address.lower() or to_address.lower() != WALLET.lower():
                user.strike += 1
                user.save()
                now = timezone.now()
                History.objects.create(user=user, title='اضافه شدن یک اخطار به دلیل تلاش برای ثبت تراکنش جعلی',
                                       description=f'کاربر در تاریخ {now} با تلاش برای ثبت تراکنش جعلی برای خرید پکیج {diamond.title} یک استرایک خورد به این دلیل که یا ولت ما در ولت مقصد نبوده و یا ولت کاربر در ولت مبدا نبوده .\nهش تراکنش : {tx_hash}',
                                       location='Transaction', type='strike')
                return Response(data={
                    'error': 'fake transaction and take strike',
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            now = timezone.now()
            History.objects.create(user=user, title='خرید ناموفق به دلیل اشکال در برسی تراکنش',
                                   description=f'کاربر در تاریخ {now} با تلاش برای ثبت تراکنش برای خرید پکیج {diamond.title} به مشکلی در پردازش تراکنش خورد .\nهش تراکنش : {tx_hash} \n پکیج : {diamond}\nمتن خطا : {e}',
                                   location='Transaction', type='warning')
            return Response(data={
                'error': 'error in verifying the transaction',
            }, status=status.HTTP_400_BAD_REQUEST)
        bnb_price = get_bnb_price()
        amount_transaction_usd = amount_transaction * bnb_price
        print(bnb_price, amount_transaction, amount_transaction_usd, (diamond.price - diamond.discount))
        if (diamond.price - diamond.discount) > amount_transaction_usd:
            now = timezone.now()
            Transaction.objects.create(tx_hash=tx_hash, user=user, amount=transaction_my_wallet['value'], status=0,
                                       for_buy=diamond)
            History.objects.create(user=user, title='خرید ناموفق به دلیل کم بودن مقدار ارسالی',
                                   description=f'کاربر در تاریخ {now} با تلاش برای ثبت تراکنش برای خرید پکیج {diamond.title} شکست خورد به این دلیل که مقدار ارسالی کافی نبوده .\nهش تراکنش : {tx_hash}',
                                   location='Transaction', type='not_enough')
            return Response(data={
                'error': 'not enough money',
            }, status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        Transaction.objects.create(tx_hash=tx_hash, user=user, amount=transaction_my_wallet['value'], status=1,
                                   for_buy=diamond)
        History.objects.create(user=user, title='خرید موفق دایموند پکیج',
                               description=f'کاربر در تاریخ {now} با تلاش برای ثبت تراکنش برای خرید پکیج {diamond.title} موفق شد و دایمند هاش از {user.diamond} به {user.diamond + diamond.value} افزایش پیدا کرد .\nهش تراکنش : {tx_hash}',
                               location='Transaction', type='buy')
        user.diamond += diamond.value
        user.save()
        News.objects.create(
            text=f'کاربر {user.username} با پرداخت {int(amount_transaction_usd)} دلار پکیج {diamond.title} را خرید و {diamond.value} دایمند گرفت .')
        return Response(data={'time': time_send.strftime('%Y-%m-%d %H:%M:%S'),
                              'from_address': from_address,
                              'to_address': to_address,
                              'amount_transaction': amount_transaction,
                              'bnb_price': get_bnb_price(),
                              'diamond_value': diamond.value
                              }, status=status.HTTP_200_OK)


d = (
    {'status': '0', 'message': 'No transactions found', 'result': []},
    {'status': '1', 'message': 'OK', 'result': [

        {'blockNumber': '38425000', 'timeStamp': '1714818177',
         'hash': '0x43ea62c92e0f32678e1e19cca347930683994d6d55f86afa49fd7054064c14ee', 'nonce': '3738049',
         'blockHash': '0x09bf5e1b2bf63e3f18ff7080f7f5c75cb5bcb3fd34e9500691af05cf3baa1f0c', 'transactionIndex': '51',
         'from': '0x1fbe2acee135d991592f167ac371f3dd893a508b', 'to': '0xd3b0d838ccceae7ebf1781d11d1bb741db7fe1a7',
         'value': '100000000000000000', 'gas': '207128', 'gasPrice': '2000000000', 'isError': '0',
         'txreceipt_status': '1', 'input': '0x', 'contractAddress': '', 'cumulativeGasUsed': '4058886',
         'gasUsed': '21000', 'confirmations': '2367978', 'methodId': '0x', 'functionName': ''},

        {'blockNumber': '39045024', 'timeStamp': '1716682361',
         'hash': '0xa635ff8a28b186e74388e7102942eeeb8fea873e1e51bb64af00af245d997239', 'nonce': '0',
         'blockHash': '0x854571d7262d20dad4779575e12e6a771e1ce9933f48ded8e46f07466418d4a1', 'transactionIndex': '67',
         'from': '0xd3b0d838ccceae7ebf1781d11d1bb741db7fe1a7', 'to': '0x0000000000000000000000000000000000001000',
         'value': '16427421502732460', 'gas': '9223372036854775807', 'gasPrice': '0', 'isError': '0',
         'txreceipt_status': '1', 'input': '0xf340fa01000000000000000000000000d3b0d838ccceae7ebf1781d11d1bb741db7fe1a7',
         'contractAddress': '', 'cumulativeGasUsed': '9682266', 'gasUsed': '68314', 'confirmations': '1747954',
         'methodId': '0xf340fa01', 'functionName': 'deposit(address accountAddress)'}
    ]
     }
)
