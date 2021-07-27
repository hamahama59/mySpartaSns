from django.shortcuts import render, redirect
from .models import UserModel
from django.http import HttpResponse
from django.contrib.auth import get_user_model #사용자가 db에 있는지 검사하는 함수
from django.contrib import auth
from django.contrib.auth.decorators import login_required


# Create your views here.
def sign_up_view(request):

    if request.method == 'GET':
        user = request.user.is_authenticated
        if user:
            return redirect('/')
        else:
            return render(request, 'user/signup.html')

    elif request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        password2 = request.POST.get('password2','')
        bio = request.POST.get('bio','')

        if password != password2:
            # 패스워드 불일치
            return render(request, 'user/signup.html',{'error':'패스워드를 확인해 주세요!'})
        else:
            if username =='' or password == '':
                return render(request, 'user/signup.html', {'error':'사용자 이름과 비밀번호는 필수 값 입니다.'})
            # 사용자 중복 유효성 검사
            other = get_user_model().objects.filter(username = username)
            if other:
                # 사용자 중복 시 리다이렉트
                return render(request, 'user/signup.html')
            else:
                # 사용자 중복 아닐 시 회원가입
                UserModel.objects.create_user(username=username,password=password,bio=bio)
                return redirect('/sign-in')

def sign_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')

        # 암호화된 pw 비교하는 문장
        me = auth.authenticate(request, username=username, password=password)

        if me is not None:
            auth.login(request, me)
            return redirect('/')
        else:
            return render(request, 'user/signin.html',{'error':'유저이름 혹은 패스워드를 확인해 주세요!'})

    elif request.method == 'GET' :
        user = request.user.is_authenticated
        if user:
            return redirect('/')
        else:
            return render(request, 'user/signin.html')


@login_required #사용자가 로그인 상태 일때만 실행되게 하는 어노테이션
def logout(request):
    auth.logout(request)
    return redirect('/')



# user/views.py
@login_required
def user_view(request):
    if request.method == 'GET':
        # 사용자를 불러오기, exclude와 request.user.username 를 사용해서 '로그인 한 사용자'를 제외하기
        user_list = UserModel.objects.all().exclude(username=request.user.username)
        return render(request, 'user/user_list.html', {'user_list': user_list})


@login_required
def user_follow(request, id):
    me = request.user
    click_user = UserModel.objects.get(id=id)
    if me in click_user.followee.all():
        click_user.followee.remove(request.user)
    else:
        click_user.followee.add(request.user)
    return redirect('/user')