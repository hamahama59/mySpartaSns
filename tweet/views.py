from django.shortcuts import render, redirect
from .models import TweetModel
from django.contrib.auth.decorators import login_required
from .models import TweetComment
from django.views.generic import ListView, TemplateView

# Create your views here.

def home(request):
    user = request.user.is_authenticated
    if user:
        return redirect('/tweet')
    else:
        return redirect('/sign-in')

def tweet(request):
    if request.method == 'GET':
        user = request.user.is_authenticated
        if user:
            all_tweet = TweetModel.objects.all().order_by('-created_at')
            return render(request, 'tweet/home.html',{'tweet':all_tweet})
         #GET 호출시 db에서 불러온 게시물 row들을 딕셔너리 형태로 'tweet'이라는 키값으로 넘김
        else:
            return redirect('/sign-in')

    elif request.method == 'POST':
        user = request.user
        content = request.POST.get('my-content','')
        tags = request.POST.get('tag','').split(',')

        if content == '':
            all_tweet = TweetModel.objects.all().order_by('-created_at')
            return render(request, 'tweet/home.html',{'error':'글을 채워 주세요!','tweet':all_tweet})

        else:
            my_tweet = TweetModel.objects.create(author=user, content=content)
            for tag in tags:
                tag = tag.strip()
                if tag != '':
                    my_tweet.tags.add(tag)
            my_tweet.save()
            return redirect('/tweet')

@login_required
def delete_tweet(request, id):
    my_tweet = TweetModel.objects.get(id=id)
    my_tweet.delete()
    return redirect('/tweet')



@login_required
def detail_tweet(request, id):
    detail_tweet = TweetModel.objects.get(id=id)
    all_comment = TweetComment.objects.filter(tweet_id=id).order_by('-created_at')
    return render(request, 'tweet/tweet_detail.html',{'tweet':detail_tweet, 'comment':all_comment})

@login_required
def write_comment(request, id):
    if request.method == 'POST':
        user = request.user
        my_comment = TweetComment()
        my_comment.tweet = TweetModel.objects.get(id=id)
        my_comment.author = user
        my_comment.comment = request.POST.get('comment','')
        my_comment.save()
        return redirect('/tweet/'+ str(id))

@login_required
def delete_comment(request, id):
    #여기서 파라미터로 넘어오는 id는 comment의 id이다.
    my_comment = TweetComment.objects.get(id=id)
    tweet_id = my_comment.tweet_id
    my_comment.delete()
    #return 할 때는 tweet의 id를 넘겨줘야 detail_tweet을 오류 없이 불러온다.
    return redirect('/tweet/'+str(tweet_id))

class TagCloudTV(TemplateView):
    template_name = 'taggit/tag_cloud_view.html'


class TaggedObjectLV(ListView):
    template_name = 'taggit/tag_with_post.html'
    model = TweetModel

    def get_queryset(self):
        return TweetModel.objects.filter(tags__name=self.kwargs.get('tag'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tagname'] = self.kwargs['tag']
        return context