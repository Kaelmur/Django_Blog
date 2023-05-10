from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from datetime import datetime
from .models import Post, Comment
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CommentForm


year = datetime.now().year


def home(request):
    return render(request, "blog/index.html", {
        "posts": Post.objects.all(),
    })


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    extra_context = {'year': year}
    context_object_name = 'posts'
    ordering = ["-date_posted"]
    paginate_by = 4


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    extra_context = {'year': year}
    context_object_name = 'posts'
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    extra_context = {'year': year}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(post=self.get_object())
        context["comments"] = comments
        if self.request.user.is_authenticated:
            context["form"] = CommentForm(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        new_comment = Comment(body=request.POST.get('body'),
                              name=self.request.user,
                              post=self.get_object())
        new_comment.save()
        return redirect(request.path_info)

    def get(self, request, *args, **kwargs):
        if request.GET.get('action') == 'delete_comment':
            return self.delete_comment(request, request.GET.get('comment_id'))
        return super().get(request, *args, **kwargs)

    def delete_comment(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id, post=self.get_object())
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect(request.path_info)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "subtitle", "image_url", "content"]
    success_url = "/"
    extra_context = {'year': year}

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["title", "subtitle", "image_url", "content"]
    success_url = "/"
    extra_context = {'update': True, 'year': year}

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    extra_context = {'year': year}
    success_url = "/"

    def form_valid(self, form):
        messages.success(self.request, 'Post deleted successfully!')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, "blog/about.html", {
        "year": year
    })


def contact(request):
    return render(request, "blog/contact.html", {
        "year": year
    })
