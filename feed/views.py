from typing import Any, Dict
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import NewPostForm, NewCommentForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DeleteView, UpdateView
from .models import Post, Comments, Likes, Tag
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json

class PostListView(ListView):
    model = Post
    template_name = "feed/home.html"
    context_object_name = "posts"
    ordering = ["-date_posted"]
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        if self.request.user.is_authenticated:
            liked = [i for i in Likes.objects.filter(user_name=self.request.user)]
            context["liked"] = liked
        return context

class UserPostListView(ListView):
    model = Post
    template_name = "feed/user_posts.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        liked = [i for i in Likes.objects.filter(user_name=self.request.user) if Likes.objects.filter(user = self.request.user, post = i)]
        context["liked"] = liked
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(user_name=user).order_by("-date_posted")
    
@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    is_liked = Likes.objects.filter(user_name=user, post=post)
    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.post = post
            data.username = user
            data.save()
            return redirect("post-detail", pk=post.pk)
    else:
        form = NewCommentForm()
    return render(request, "feed/post_detail.html", {"post": post, "is_liked": is_liked, "form": form})

@login_required
def create_post(request):
    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.user_name = request.user
            data.save()
            messages.success(request, f"Posted successfully")
            return redirect("home")
    else:
        form = NewPostForm()
    return render(request, "feed/create_post.html", {"form": form})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["description", "pic", "tags"]
    template_name = "feed/create_post.html"

    def form_valid(self, form):
        form.instance.user_name = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user_name:
            return True
        return False
    
@login_required
def post_delete(request, pk):
    post = Post.objects.get(pk=pk)
    if request.user == post.user_name:
        Post.objects.get(pk=pk).delete()
    return redirect("home")

@login_required
def search_posts(request):
    query = request.GET.get("p")
    object_list = Post.objects.filter(tags__icontains=query)
    liked = [i for i in object_list if Likes.objects.filter(user = request.user, post = i)]
    context = {"posts": object_list, "liked": liked}
    return render(request, "feed/search_posts.html", context)

@login_required
def like(request):
    post_id = request.GET.get("likeId", "")
    user = request.user
    post = Post.objects.get(pk=post_id)
    liked = False
    like = Likes.objects.filter(user_name=user, post=post)
    if like:
        like.delete()
    else:
        liked = True
        Likes.objects.create(user_name=user, post=post)
    resp = {
        "liked": liked
    }
    response = json.dumps(resp)
    return HttpResponse(response, content_type = "application/json")