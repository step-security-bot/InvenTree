"""Mixins for (API) views in the whole project."""

from accu.accu.core.clean.mixin import CleanMixin
from rest_framework import generics


class ListAPI(generics.ListAPIView):
    """View for list API."""


class ListCreateAPI(CleanMixin, generics.ListCreateAPIView):
    """View for list and create API."""


class CreateAPI(CleanMixin, generics.CreateAPIView):
    """View for create API."""


class RetrieveAPI(generics.RetrieveAPIView):
    """View for retreive API."""
    pass


class RetrieveUpdateAPI(CleanMixin, generics.RetrieveUpdateAPIView):
    """View for retrieve and update API."""
    pass


class RetrieveUpdateDestroyAPI(CleanMixin, generics.RetrieveUpdateDestroyAPIView):
    """View for retrieve, update and destroy API."""


class UpdateAPI(CleanMixin, generics.UpdateAPIView):
    """View for update API."""
