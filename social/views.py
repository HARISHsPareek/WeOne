from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostForm
from django.db.models import Q

from social import models, forms

# Create your views here.
class Wall(LoginRequiredMixin, ListView):
  context_object_name = 'posts'
  template_name = 'social/wall.html'
  login_url = 'auth/login'

  def get_queryset(self):
    friendIds = [ friend.person2.id for friend in  models.Friends.objects.filter(person1 = self.request.user) ]
    friendIds = friendIds + [ friend.person1.id for friend in  models.Friends.objects.filter(person2 = self.request.user) ]

    return models.Post.objects.filter(user__in = friendIds).order_by('-created_at')

class Home(LoginRequiredMixin, ListView):
  context_object_name = 'posts'
  template_name = 'social/home.html'
  login_url = 'auth/login'

  def get_queryset(self):
    return models.Post.objects.filter(user = self.request.user)
  
  def get_context_data(self, *args, **kwargs):
    data = super().get_context_data(*args, **kwargs)
    data['post_form'] = forms.PostForm()

    return data

class Post(View):
  def post(self, request):
    form = forms.PostForm(request.POST, request.FILES)
    if form.is_valid():
      post = form.save(commit=False)
      post.user = request.user
      post.save()
    
    return redirect('/home/')
  
class PostUpdateView(View):
    def get(self, request, pk):
        post = get_object_or_404(models.Post, pk=pk, user=request.user)
        form = PostForm(instance=post)
        return render(request, 'social/postedit.html', {'form': form, 'post': post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, user=request.user)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('/home/')
        return render(request, 'social/postedit.html', {'form': form, 'post': post})


class PostLike(View):
  model = models.Post

  def post(self, request, pk):
    post = self.model.objects.get(pk = pk)
    models.Like.objects.create(post = post, user = request.user)
    return HttpResponse(code = 204)

class PostComment(View):
  model = models.Post
  form = forms.PostComment

  def post(self, request, pk):
    post = self.model.objects.get(pk = pk)
    form = self.form(request.POST)

    if form.is_valid():
      comment = form.save(commit = False)
      comment.post = post
      comment.user = request.user
      comment.save()
      return HttpResponse(code = 204)
    
    print(form.errors)
    return HttpResponse('Error')