from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Reply
from .forms import PostForm, ReplyForm
from django.contrib import messages
@login_required
def forums_home(request):
    posts = Post.objects.all().order_by('-created_at')[:10]  # Fetch the most recent 10 posts
    return render(request, 'forums/forums_home.html', {'posts': posts})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    replies = post.replies.all().order_by('-created_at')
    reply_form = ReplyForm()

    if request.method == 'POST':
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.author = request.user
            reply.post = post
            reply.save()
            return redirect('post_detail', post_id=post.id)

    return render(request, 'forums/post_detail.html', {'post': post, 'replies': replies, 'reply_form': reply_form})

@login_required
def create_post(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('forums_home')

    return render(request, 'forums/create_post.html', {'form': form})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)  # Unlike the post
    else:
        post.likes.add(request.user)  # Like the post
    return redirect('forums_home')
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.delete()
        messages.success(request, "Post deleted successfully!")
    else:
        messages.error(request, "You are not allowed to delete this post.")
    return redirect('forums_home')

@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if request.user == reply.author:
        reply.delete()
        messages.success(request, "Reply deleted successfully!")
    else:
        messages.error(request, "You are not allowed to delete this reply.")
    return redirect('post_detail', post_id=reply.post.id)
@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'forums/my_posts.html', {'posts': posts})

@login_required
def my_replies(request):
    replies = Reply.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'forums/my_replies.html', {'replies': replies})

@login_required
def my_likes(request):
    liked_posts = Post.objects.filter(likes=request.user).order_by('-created_at')
    return render(request, 'forums/my_likes.html', {'liked_posts': liked_posts})