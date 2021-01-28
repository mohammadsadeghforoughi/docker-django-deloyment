from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Post, Category, CommentLike, Comment
from .forms import CommentForm, CommentLikeForm
from datetime import datetime
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

User = get_user_model()


class PostArchive(LoginRequiredMixin, ListView):
    model = Post
    queryset = Post.objects.filter(
        draft=False, publish_time__lte=datetime.now())
    ordering = ('publish_time',)
    template_name = 'blog/post_archive.html'


class CategoryDetails(DetailView):
    model = Category
    template_name = 'blog/category_single.html'


class PostDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Post
    permission_required = ('blog.view_post', 'blog.comment_view')
    template_name = 'blog/post_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        context['comments'] = post.comments.all()
        context['setting'] = post.post_setting
        return context


@login_required
@permission_required('blog.view_post')
def home(request):
    author = request.GET.get('author', None)
    category = request.GET.get('category', None)
    posts = Post.objects.all()
    if author:
        posts = posts.filter(author__username=author)
    if category:
        posts = posts.filter(category__slug=category)
    categories = Category.objects.all()
    context = {
        "posts": posts,
        "categories": categories,
    }
    return render(request, 'blog/posts.html', context)


@csrf_exempt
def like_comment(request):
    data = json.loads(request.body)
    user = request.user
    try:
        comment = Comment.objects.get(id=data['comment_id'])
    except Comment.DoesNotExist:
        return HttpResponse('bad request', status=404)
    try:
        comment_like = CommentLike.objects.get(author=user, comment=comment)
        comment_like.condition = data['condition']
        comment_like.save()
    except CommentLike.DoesNotExist:
        CommentLike.objects.create(
            author=user, condition=data['condition'], comment=comment)
    response = {"like_count": comment.like_count,
                'dislike_count': comment.dislike_count}
    return HttpResponse(json.dumps(response), status=201)


@csrf_exempt
def create_comment(request):
    data = json.loads(request.body)
    user = request.user
    try:
        comment = Comment.objects.create(
            post_id=data['post_id'], content=data['content'], author=user)
        response = {"comment_id": comment.id, "content": comment.content, 'dislike_count': 0, 'like_count': 0,
                    'full_name': user.get_full_name()}
        return HttpResponse(json.dumps(response), status=201)
    except:
        response = {"error": 'error'}
        return HttpResponse(json.dumps(response), status=400)


def post_single(request, slug):
    try:
        post = Post.objects.select_related(
            'post_setting', 'category', 'author').get(slug=slug)
    except Post.DoesNotExist:
        raise Http404('post not found')
    context = {
        'form': CommentForm(),
        "post": post,
        'settings': post.post_setting,
        'category': post.category,
        'author': post.author,
        'comments': post.comments.filter(is_confirmed=True)
    }
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
        else:
            context['form'] = form

    return render(request, 'blog/post_single.html', context)


def category_single(request, pk):
    try:
        category = Category.objects.get(slug=pk)
    except Category.DoesNotExist:
        raise Http404('Category not found')
    posts = Post.objects.filter(category=category)
    links = ''.join(
        '<li><a href={}>{}</a></li>'.format(reverse('post_single', args=[post.slug]), post.title) for post in posts)
    blog = '<html><head><title>post archive</title></head>{}<a href={}>all categories</a></body></html>'.format(
        '<ul>{}</ul>'.format(links), reverse('categories_archive'))
    return HttpResponse(blog)


def categories_archive(request):
    categories = Category.objects.all()
    links = ''.join(
        '<li><a href={}>{}</a></li>'.format(reverse('category_single', args=[category.slug]), category.title) for
        category in categories)
    blog = '<html><head><title>post archive</title></head>{}</body></html>'.format(
        '<ul>{}</ul>'.format(links))
    return HttpResponse(blog)
