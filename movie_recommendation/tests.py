from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Favorite, Movie, Rating, SearchHistory, User, Watchlist

# Helpers


def make_user(username, email, password="testpass123"):
    return User.objects.create_user(username=username, email=email, password=password)


def get_token(client, username, password="testpass123"):
    res = client.post(
        reverse("token_obtain_pair"), {"username": username, "password": password}
    )
    return res.data["access"]


def auth(client, token):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


def make_movie(tmdb_id=1, title="Inception"):
    return Movie.objects.create(tmdb_id=tmdb_id, title=title)


# Auth


class AuthTests(APITestCase):

    def test_register(self):
        res = self.client.post(
            reverse("register"),
            {
                "username": "denis",
                "email": "denis@test.com",
                "password": "pass1234",
                "first_name": "Denis",
                "last_name": "K",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_login_returns_tokens(self):
        make_user("denis", "denis@test.com")
        res = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "denis", "password": "testpass123"},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)

    def test_wrong_password_rejected(self):
        make_user("denis", "denis@test.com")
        res = self.client.post(
            reverse("token_obtain_pair"), {"username": "denis", "password": "wrong"}
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Movies


class MovieTests(APITestCase):

    def test_anyone_can_fetch_movies(self):
        res = self.client.get(reverse("movie-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)


# Favorites


class FavoriteTests(APITestCase):

    def setUp(self):
        self.user = make_user("denis", "denis@test.com")
        self.token = get_token(self.client, "denis")
        self.movie = make_movie()

    def test_user_can_add_favorite(self):
        auth(self.client, self.token)
        res = self.client.post(
            f"/api/users/{self.user.id}/favorites/", {"movie_id": self.movie.id}
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_can_list_favorites(self):
        Favorite.objects.create(user=self.user, movie=self.movie)
        auth(self.client, self.token)
        res = self.client.get(f"/api/users/{self.user.id}/favorites/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_add_favorite(self):
        res = self.client.post(
            f"/api/users/{self.user.id}/favorites/", {"movie_id": self.movie.id}
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Watchlist


class WatchlistTests(APITestCase):

    def setUp(self):
        self.user = make_user("denis", "denis@test.com")
        self.token = get_token(self.client, "denis")
        self.movie = make_movie(tmdb_id=2, title="Interstellar")

    def test_user_can_add_to_watchlist(self):
        auth(self.client, self.token)
        res = self.client.post(
            f"/api/users/{self.user.id}/watchlist/", {"movie_id": self.movie.id}
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_can_list_watchlist(self):
        Watchlist.objects.create(user=self.user, movie=self.movie)
        auth(self.client, self.token)
        res = self.client.get(f"/api/users/{self.user.id}/watchlist/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)


# Ratings


class RatingTests(APITestCase):

    def setUp(self):
        self.user = make_user("denis", "denis@test.com")
        self.token = get_token(self.client, "denis")
        self.movie = make_movie(tmdb_id=3, title="The Dark Knight")

    def test_user_can_rate_movie(self):
        auth(self.client, self.token)
        res = self.client.post(
            f"/api/users/{self.user.id}/ratings/",
            {"movie_id": self.movie.id, "rating": 4.5},
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_can_list_ratings(self):
        Rating.objects.create(user=self.user, movie=self.movie, rating=4.5)
        auth(self.client, self.token)
        res = self.client.get(f"/api/users/{self.user.id}/ratings/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)


# Search History


class SearchTests(APITestCase):

    def setUp(self):
        self.user = make_user("denis", "denis@test.com")
        self.token = get_token(self.client, "denis")

    def test_user_can_search(self):
        auth(self.client, self.token)
        res = self.client.post(reverse("searchhistory-list"), {"query": "inception"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_can_view_search_history(self):
        SearchHistory.objects.create(user=self.user, query="inception")
        auth(self.client, self.token)
        res = self.client.get(reverse("searchhistory-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_search(self):
        res = self.client.post(reverse("searchhistory-list"), {"query": "inception"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
