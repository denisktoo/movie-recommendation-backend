from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import viewsets, permissions, mixins, status, generics
from .models import (
    User, Favorite, Watchlist, Rating, SearchHistory,
    RecommendationCache
)
from .serializer import (
    RegisterSerializer, UserSerializer, MovieSerializer, FavoriteSerializer,
    WatchlistSerializer, RatingSerializer, SearchHistorySerializer,
    RecommendationCacheSerializer
)
from .permissions import IsAdminOrReadOnly, IsAuthenticatedOwnerOrAdmin
from .tmdb import fetch_and_cache_trending_movies
from django_filters.rest_framework import DjangoFilterBackend
from .filter import MovieFilter
from rest_framework.decorators import action
from .recommendation_service import (
    recommend_from_search_history,
    recommend_from_ratings,
)
from .tasks import registration_confirmation_email


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOwnerOrAdmin]

    def get_queryset(self):
        """
        Admin sees all users.
        Normal users only see themselves.
        """
        if getattr(self.request.user, "role", None) == "admin":
            return User.objects.all().order_by("id")

        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        try:
            if getattr(self.request.user, "role", None) == "admin":
                # Admin can change role
                serializer.save(allow_role_change=True)
            else:
                # Normal users cannot change role
                serializer.save(role=self.get_object().role)
        except DjangoValidationError as exc:
            raise ValidationError({"detail": str(exc)})


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MovieSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MovieFilter

    def get_queryset(self):
        return fetch_and_cache_trending_movies()


class OwnedResourceViewSet(viewsets.ModelViewSet):
    """
    Base viewset for resources owned by a user.
    Child classes must define:
    - model_class
    - serializer_class
    """
    permission_classes = [IsAuthenticatedOwnerOrAdmin]
    model_class = None

    def get_queryset(self):
        """
        Admin can see all.
        Normal users only see their own records.
        """
        user = self.request.user

        if getattr(user, "role", None) == "admin":
            return self.model_class.objects.all().order_by("-id")

        return self.model_class.objects.filter(user=user).order_by("-id")

    def perform_create(self, serializer):
        """
        Always attach the authenticated user.
        Prevents a user from creating data under another person's account.
        """
        try:
            serializer.save(user=self.request.user)

        except IntegrityError:
            raise ValidationError({
                "detail": "This item already exists in your account."
            })

        except DjangoValidationError as exc:
            raise ValidationError({"detail": str(exc)})


class FavoriteViewSet(OwnedResourceViewSet):
    serializer_class = FavoriteSerializer
    model_class = Favorite


class WatchlistViewSet(OwnedResourceViewSet):
    serializer_class = WatchlistSerializer
    model_class = Watchlist


class RatingViewSet(OwnedResourceViewSet):
    serializer_class = RatingSerializer
    model_class = Rating

    def perform_create(self, serializer):
        try:
            rating_value = serializer.validated_data.get("rating")

            if rating_value is not None and not (0 <= rating_value <= 5):
                raise ValidationError({
                    "rating": "Please provide a rating between 0 and 5."
                })

            serializer.save(user=self.request.user)

        except IntegrityError:
            raise ValidationError({
                "detail": (
                    "You have already rated this movie."
                    "Please update your existing rating instead."
                )
            })

        except DjangoValidationError as exc:
            raise ValidationError({"detail": str(exc)})

    def perform_update(self, serializer):
        rating_value = serializer.validated_data.get("rating")

        if rating_value is not None and not (0 <= rating_value <= 5):
            raise ValidationError({
                "rating": "Please provide a rating between 0 and 5."
            })

        serializer.save()


class SearchHistoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SearchHistory.objects.filter(
            user=self.request.user
        ).order_by("-searched_at")

    def perform_create(self, serializer):
        query = serializer.validated_data.get("query", "").strip()

        if not query:
            raise ValidationError({
                "query": "Please enter a search term."
            })

        serializer.save(user=self.request.user)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        deleted_count, _ = self.get_queryset().delete()

        if deleted_count == 0:
            return Response(
                {"detail": "Your search history is already empty."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Your search history has been cleared."},
            status=status.HTTP_200_OK
        )


class RecommendationCacheViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RecommendationCacheSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecommendationCache.objects.filter(
            user=self.request.user
        ).order_by("-updated_at")


class RecommendationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="from-search-history")
    def from_search_history(self, request):
        movies = recommend_from_search_history(request.user, limit=10)
        serializer = MovieSerializer(movies, many=True)

        if not movies:
            return Response(
                {
                    "detail": (
                        "No recommendations were found from your recent searches yet."
                        "Try searching for a few movies or genres first."
                    ),
                    "results": []
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="from-ratings")
    def from_ratings(self, request):
        movies = recommend_from_ratings(request.user, limit=10)
        serializer = MovieSerializer(movies, many=True)

        if not movies:
            return Response(
                {
                    "detail": (
                        "No recommendations were found from your ratings yet. Rate a"
                        "few movies first to get personalized suggestions."
                    ),
                    "results": []
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        transaction.on_commit(
            lambda: registration_confirmation_email.delay(user.id)
        )
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        return Response(
            {
                "detail": "Your account has been created successfully.",
                "user": RegisterSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )
