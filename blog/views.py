from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from markdownx.utils import markdownify
from .forms import ArticleForm, CategoryForm, TagForm
from .models import Article, Tag, Category

def home(request):
    request.session['current_page'] = 'blog'
    art_list = Article.objects.filter(published=True, featured=True)
    paginator = Paginator(art_list, 7, orphans=3)

    # Populate tag cloud
    tags = Tag.objects.annotate(total=Count('article', filter=Q(article__published=True))).filter(total__gt=0)
    average = Tag.objects.annotate(total=Count('article', filter=Q(article__published=True))).aggregate(average_total=Avg('total'))['average_total']
    # min weight (in rem) is 1, while max weight is 3
    weight = []
    for t in tags:
        w = t.total/average if average > 0 else 0
        w = float('{0:.2f}'.format(w))
        if w > 3:
            w = 3
        weight.append(w if w >= 1 else 1)
    #print('weights: {}'.format(weight))
    tags = zip(tags, weight)

    # Get all categories
    categories = Category.objects.annotate(total=Count('article'))
    
    page = request.GET.get('page')
    arts = paginator.get_page(page)
    return render(request, 'blog/home.html', {
        'arts': arts,
        'pop_arts': _get_hot_articles(),
        'tags': tags,
        'cats': categories,
        'debug': settings.DEBUG,
    })

def article(request, year, slug):
    """Render an article."""
    art = get_object_or_404(Article, date_created__year=year, slug=slug)
    # redirect to homepage if the art is not published
    if not art.published:
        return redirect('blog:home')
    art_content_html = markdownify(art.content)
    response = render(request, 'blog/article.html', {
        'art': art,
        'art_content_html': art_content_html,
        'pop_arts': _get_hot_articles(),
        'debug': settings.DEBUG,
    })
    # update article's view count using cookies
    if request.COOKIES.get(art.slug) is None and not request.user.is_authenticated:
        import datetime
        now = datetime.datetime.now()
        three_days = now + datetime.timedelta(days=3)
        response.set_signed_cookie(art.slug, art.id, expires=three_days)
        art.view_count = F('view_count') + 1
        art.save()
    return response

@login_required
def create(request):
    """Create a new article."""
    request.session['current_page'] = 'blog'
    if request.method == 'GET':
        form = ArticleForm()
        return render(request, 'blog/create.html', {
            'form': form,
        })
    elif request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            art = form.save()
            # ping search engine
            _ping(art.title, '{}{}'.format(request.get_host(), art.get_absolute_url()))
            # update sitemap
            _update_sitemap(request.get_host())
            return redirect(art)
        else:
            return render(request, 'blog/create.html', {
                'form': form,
            })

@login_required
def edit(request, year, slug):
    """Edit the article."""
    request.session['current_page'] = 'blog'
    art = get_object_or_404(Article, date_created__year=year, slug=slug)
    art_year = art.date_created.year
    art_slug = art.slug
    if request.method == 'POST':
        # Use POST data to update a model instance
        form = ArticleForm(request.POST, instance=art)
        if form.is_valid():
            art = form.save()
            # ping the blog
            _ping(art.title, '{}{}'.format(request.get_host(), art.get_absolute_url()))
            # update sitemap
            _update_sitemap(request.get_host())
            return redirect(art)
    else:
        form = ArticleForm(instance=art)
    return render(request, 'blog/edit.html', {
        'form': form,
        'art_year': art_year,
        'art_slug': art_slug,
    })

@login_required
def delete(request, year, slug):
    """Ask for confirmation before deletion."""
    request.session['current_page'] = 'blog'
    art = get_object_or_404(Article, date_created__year=year, slug=slug)
    return render(request, 'blog/delete.html', {
        'art': art,
    })

@login_required
def delete_commit(request):
    """Delete the article."""
    if request.method == 'POST':
        art_id = request.POST.get('article-id')
        art = get_object_or_404(Article, id=art_id)
        art.delete()
        # update sitemap
        _update_sitemap(request.get_host())
        return redirect('blog:home')
    return redirect('blog:home')

@login_required
def publish(request):
    """Publish (or unpublish) the article."""
    if request.method == 'POST':
        art_year = request.POST.get('article-year')
        art_slug = request.POST.get('article-slug')
        art = get_object_or_404(Article, date_created__year=art_year, slug=art_slug)
        art.published = not art.published
        art.save()
        # update sitemap
        _update_sitemap(request.get_host())
        redirect_to = request.POST.get('origin-path')
        if redirect_to:
            return redirect(redirect_to)
        else:
            return redirect('blog:home')
    return redirect('blog:home')

@login_required
def list_all(request):
    """Render all existing articles using table."""
    art_list = Article.objects.all()
    paginator = Paginator(art_list, 20, orphans=3)

    page = request.GET.get('page')
    arts = paginator.get_page(page)
    return render(request, 'blog/list.html', {
        'arts': arts,
    })

def tag(request, name):
    tag = get_object_or_404(Tag, name=name)
    art_list = Article.objects.filter(tag=tag, published=True)
    paginator = Paginator(art_list, 10, orphans=3)

    page = request.GET.get('page')
    arts = paginator.get_page(page)
    return render(request, 'blog/tag.html', {
        'arts': arts,
        'tag_name': tag.name,
        'debug': settings.DEBUG,
    })

@login_required
def tag_create(request):
    tags = Tag.objects.all()
    if request.method == 'GET':
        form = TagForm()
        return render(request, 'blog/tag-create.html', {
            'form': form,
            'tags': tags,
        })
    elif request.method == 'POST':
        post = request.POST.copy()
        if 'name' in post:
            post['name'] = slugify(str(post['name']))
        form = TagForm(post)
        if form.is_valid():
            form.save()
            return redirect('blog:tag-create')
        else:
            return render(request, 'blog/tag-create.html', {
                'form': form,
                'tags': tags,
            })

@login_required
def tag_edit(request, name):
    tag = get_object_or_404(Tag, name=name)
    tag_name = tag.name
    if request.method == 'POST':
        post = request.POST.copy()
        if 'name' in post:
            post['name'] = slugify(str(post['name']))
        form = TagForm(post, instance=tag)
        if form.is_valid():
            form.save()
            return redirect('blog:tag-create')
    else:
        form = TagForm(instance=tag)
    return render(request, 'blog/tag-edit.html', {
        'form': form,
        'tag_name': tag_name,
    })

def category(request, name):
    category = get_object_or_404(Category, name=name)
    art_list = Article.objects.filter(category=category, published=True)
    paginator = Paginator(art_list, 10, orphans=3)

    page = request.GET.get('page')
    arts = paginator.get_page(page)
    return render(request, 'blog/category.html', {
        'arts': arts,
        'category_name': category.name,
        'debug': settings.DEBUG,
    })

@login_required
def category_create(request):
    cats = Category.objects.all()
    if request.method == 'GET':
        form = CategoryForm()
        return render(request, 'blog/category-create.html', {
            'form': form,
            'cats': cats,
        })
    elif request.method == 'POST':
        post = request.POST.copy()
        if 'name' in post:
            post['name'] = slugify(str(post['name']))
        form = CategoryForm(post)
        if form.is_valid():
            form.save()
            return redirect('blog:category-create')
        else:
            return render(request, 'blog/category-create.html', {
                'form': form,
                'cats': cats,
            })

@login_required
def category_edit(request, name):
    cat = get_object_or_404(Category, name=name)
    cat_name = cat.name
    if request.method == 'POST':
        post = request.POST.copy()
        if 'name' in post:
            post['name'] = slugify(str(post['name']))
        form = CategoryForm(post, instance=cat)
        if form.is_valid():
            form.save()
            return redirect('blog:category-create')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'blog/category-edit.html', {
        'form': form,
        'cat_name': cat_name,
    })

def search(request):
    """Show search result."""
    request.session['current_page'] = 'blog'
    if request.method == 'POST':
        search_term = str(request.POST.get('search-term')).strip()
        found_art_list = Article.objects.filter((Q(title__contains=search_term) | Q(summary__contains=search_term)) & Q(published=True))
        paginator = Paginator(found_art_list, 10, orphans=3)

        page = request.GET.get('page')
        found_arts = paginator.get_page(page)
        return render(request, 'blog/search-result.html', {
            'arts': found_arts,
            'search_term': search_term,
            'debug': settings.DEBUG,
        })
    return redirect('blog:home')

def about(request):
    request.session['current_page'] = 'about'
    return render(request, 'blog/about.html')

def login_view(request):
    if request.method == 'GET':
        # redirect if already logged in
        if request.user.is_authenticated:
            return redirect('blog:home')
        next_page = request.GET.get('next') or ''
        return render(request, 'blog/login.html', {
            'next': next_page,
        })
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            redirect_to = request.POST.get('next')
            if redirect_to:
                return redirect(redirect_to)
            else:
                return redirect('blog:home')
        else:
            return redirect('blog:login')

@login_required
def logout_view(request):
    logout(request)
    return redirect('blog:home')

def _get_hot_articles():
    """Get most popular articles, ordered by view count and date (both descending)."""
    hot_arts = Article.objects.filter(published=True, featured=True).order_by('-view_count', '-date_created')[:15]
    return hot_arts

def _ping(title, url):
    """Ping search engines whenever an article is created/edited/deleted.
    Using url encoded params.\n
    Params: \n
    - title: Article's title\n
    - url: Article's canonical url (excluding schema)
    """
    import urllib.parse, requests
    title = urllib.parse.quote_plus(title)
    url = urllib.parse.quote_plus(url)
    try:
        pingomatic = 'https://pingomatic.com/ping/?title={}&blogurl=https%3A%2F%2F{}&rssurl=http%3A%2F%2F&chk_weblogscom=on&chk_blogs=on&chk_feedburner=on&chk_newsgator=on&chk_myyahoo=on&chk_pubsubcom=on&chk_blogdigger=on&chk_weblogalot=on&chk_newsisfree=on&chk_topicexchange=on&chk_google=on&chk_tailrank=on&chk_skygrid=on&chk_collecta=on&chk_superfeedr=on'.format(title, url)
        print('Pinging address {}'.format(pingomatic))
        r = requests.get(pingomatic)
        print('Ping blog status code: {}'.format(r.status_code))
    except:
        print('Could not ping.')

def _update_sitemap(hostname):
    """Update sitemap when an article is added/edited/deleted.\n
    Params:\n
    hostname: just use 'request.get_host()'
    """
    with open(settings.SITEMAP_LOCATION, 'w') as sitemap:
        homepage = '{}/'.format(hostname)
        about_page = '{}about/'.format(homepage)
        sitemap.write('{}\n{}\n'.format(homepage, about_page))
        
        artsx = Article.objects.filter(published=True)[:9998]
        for artx in artsx:
            sitemap.write('{}{}\n'.format(hostname, artx.get_absolute_url()))
