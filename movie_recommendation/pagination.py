from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle


class BasePagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


class RecommendationsThrottle(UserRateThrottle):
    """
    Custom throttle for recommendation endpoints.
    These hit the TMDB API and run heavy DB queries.
    Limited to 20 requests per hour per user.
    """

    scope = "recommendations"
