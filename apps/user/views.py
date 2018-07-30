from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from user.models import User
from django.conf import settings
from django.http import HttpResponse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import re


# Create your views here.


# /user/register
# def register(request):
#     """显示注册页面"""
#     if request.method == "GET":
#         # 显示注册页面
#         return render(request, 'register.html')
#     else:
#         # 接收数据
#         username = request.POST.get('user_name')
#         password = request.POST.get('pwd')
#         email = request.POST.get('email')
#         allow = request.POST.get('allow')
#         # 进行数据校验
#         if not all([username, password, email]):
#             # 数据不完整
#             return render(request, 'register.html', {'errmsg': '数据不完整'})
#
#         # 校验邮箱
#         if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#             return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
#         if allow != 'on':
#             return render(request, 'register.html', {'errmsg': '请同意用户协议'})
#
#         # 校验用户名是否重名
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             # 用户名不存在
#             user = None
#         if user:
#             # 用户名已存在
#             return render(request, 'register.html', {'errmsg': '用户名已存在'})
#
#         # 进行业务处理：进行用户注册
#         user = User.objects.create_user(username, email, password)
#         user.is_active = 0
#         user.save()
#         # 返回应答,跳转到首页
#         return redirect(reverse('goods:index'))


# def register_handle(request):
#     """进行注册处理"""
#     # 接收数据
#     username = request.POST.get('user_name')
#     password = request.POST.get('pwd')
#     email = request.POST.get('email')
#     allow = request.POST.get('allow')
#     # 进行数据校验
#     if not all([username, password, email]):
#         # 数据不完整
#         return render(request, 'register.html', {'errmsg': '数据不完整'})
#
#     # 校验邮箱
#     if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#         return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
#     if allow != 'on':
#         return render(request, 'register.html', {'errmsg': '请同意用户协议'})
#
#     # 校验用户名是否重名
#     try:
#         user = User.objects.get(username=username)
#     except User.DoesNotExist:
#         # 用户名不存在
#         user = None
#     if user:
#         # 用户名已存在
#         return render(request, 'register.html', {'errmsg':'用户名已存在'})
#
#     # 进行业务处理：进行用户注册
#     user = User.objects.create_user(username,email,password)
#     user.is_active = 0
#     user.save()
#     # 返回应答,跳转到首页
#     return redirect(reverse('goods:index'))

# /user/register
# GET POST 类视图处理不同的请求方式
class RegisterView(View):
    """注册"""

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意用户协议'})

        # 校验用户名是否重名
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件,包含激活链接:http:127.0.0.1:8000/user/active/1
        # 激活链接中需要包含用户的身份信息,并且要把身份信息进行加密
        # 加密用户的身份信息,生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)

        # 发送激活邮件
        # 返回应答,跳转到首页
        return redirect(reverse('goods:index'))


class ActiveView(View):
    """用户激活"""

    def get(self, request, token):
        """进行用户激活"""
        # 进行解密
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse("激活链接已过期")


# /user/login
class LoginView(View):
    """登录"""

    def get(self, request):
        """显示登录页面"""
        return render(request, 'login.html')
