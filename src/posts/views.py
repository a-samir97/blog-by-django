from django.db.models import Count,Q
from django.shortcuts import render, get_object_or_404, reverse,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post,Author,PostView
from .forms import CommentForm, PostForm
from marketing.models import Subscribe

def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if  query:
        queryset = queryset.filter(
            Q(title__icontains=query)|
            Q(overview__icontains=query)
        ).distinct()

    context = {'queryset':queryset}
    return render(request,'search_results.html',context)

def get_count_categories():
    queryset = Post.objects.values('categories__title').annotate(Count('categories__title'))
    return queryset

def home(request):
    items = Post.objects.filter(featured=True)[0:3]
    latest = Post.objects.order_by('-timestamp')[0:3]

    if request.method == 'POST':
        email = request.POST['email']
        new_subscribe = Subscribe()
        new_subscribe.email = email
        new_subscribe.save()
        
    return render(request,'index.html',{'items':items,'latest':latest,})

def blog(request):
    category_count = get_count_categories()
    latest = Post.objects.order_by('-timestamp')[:3]
    post_list = Post.objects.all()
    paginator = Paginator(post_list,4)
    page_request = 'page'
    page = request.GET.get(page_request)
    try:
        paginated_query = paginator.page(page)
    except PageNotAnInteger:
        paginated_query = paginator.page(1)
    except EmptyPage:
        paginated_query = paginator.page(paginator.num_pages)

    context = {
        'queryset':paginated_query,
        'page_request':page_request,
        'latest':latest,
        'category_count':category_count,
    }
    return render(request,'blog.html',context)

def post(request,id):
    post = get_object_or_404(Post,id=id)
    category_count = get_count_categories()
    latest = Post.objects.order_by('-timestamp')[:3]
    PostView.objects.get_or_create(user=request.user,post=post)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse('post-detail',kwargs={'id':id}))
    context = {
        'post':post,
        'latest':latest,
        'category_count':category_count,
        'form':form
    }
    return render(request,'post.html',context)

def post_create(request):
    title = "Create"
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse('post-detail',kwargs={"id": form.instance.id}))
    context = {
        'title':title,
        'form':form,
    }
    return render(request,'post_create.html',context)

def post_update(request,id):
    title = 'Update'
    post = get_object_or_404(Post,id=id)
    form = PostForm(request.POST or None, request.FILES or None,instance=post)
    author = get_author(request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse('post-detail',kwargs={"id": form.instance.id}))
    context = {
        'title':title,
        'form':form,
    }
    return render(request,'post_create.html',context)

def post_delete(request,id):
    post = get_object_or_404(Post,id=id)
    post.delete()
    return redirect(reverse('post-list'))