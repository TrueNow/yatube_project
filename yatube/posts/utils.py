from django.core.paginator import Paginator

PAGINATE_BY: int = 10


def get_page_obj(request, posts_list):
    paginator = Paginator(posts_list, PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
