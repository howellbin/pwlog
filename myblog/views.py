import markdown
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.views.generic import ListView, DetailView
from markdown.extensions.toc import TocExtension

from .models import Post, Category, Tag

MONTH_NAME_MAP = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}


class PostDetailView(DetailView):
    model = Post
    template_name = 'myblog/detail.html'
    context_object_name = 'post'
    queryset = Post.objects.all()

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify=slugify)
        ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post


class IndexView(ListView):
    model = Post
    template_name = 'myblog/index.html'
    context_object_name = 'post_list'
    paginate_by = 5
    title = 'Blog | Jian Yang'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator, page, is_paginated)
        context.update(pagination_data)
        context.update({
            'title': self.title,
        })
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}

        left = []
        right = []
        left_has_more = False
        right_has_more = False
        first = False
        last = False

        page_number = page.number
        total_pages = paginator.num_pages
        page_range = paginator.page_range

        if page_number != 1:
            left = page_range[(page_number - 3)
                              if (page_number - 3) > 0 else 0:page_number - 1]
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        if page_number != total_pages:
            right = page_range[page_number:page_number + 2]
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last
        }
        return data


class ArchivesView(IndexView):
    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        self.title = MONTH_NAME_MAP[month] + ' ' + str(year) + ' | 存在与虚无'
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year,
                                                               created_time__month=month)


class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        self.title = cate.name + ' | 存在与虚无'
        return super(CategoryView, self).get_queryset().filter(category=cate)


class TagView(IndexView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        self.title = tag.name + ' | 存在与虚无'
        return super(TagView, self).get_queryset().filter(tags=tag)
