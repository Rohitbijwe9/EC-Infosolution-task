from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Book
from .serializer import BookSerializer
import requests

class CustomPagination(PageNumberPagination):
    page_size = 20

class BookList(generics.ListAPIView):
    serializer_class = BookSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        filter_criteria = self.request.query_params.get('filter_criteria', '')
        if filter_criteria:
            books_data = self.fetch_books(filter_criteria)
            if not books_data or 'results' not in books_data:
                return Book.objects.none()
            self.save_books(books_data)
            queryset = self.filter_books(filter_criteria)
        else:
            queryset = Book.objects.all()
        return queryset

    def fetch_books(self, filter_criteria):
        url = 'https://gutendex.com/books/'
        params = {'search': filter_criteria}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for non-200 status codes
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"Error fetching books data: {e}")
            return None

    def save_books(self, books_data):
        for book_data in books_data['results']:
            language_code = book_data.get('languages', [])[0].get('code') if book_data.get('languages') else ''
            Book.objects.create(
                title=book_data['title'],
                author=book_data['authors'][0]['name'] if book_data.get('authors') else '',
                genre=book_data['bookshelves'][0] if book_data.get('bookshelves') else '',
                language=language_code,
                subjects=', '.join(book_data['subjects']) if book_data.get('subjects') else '',
                bookshelves=', '.join(book_data['bookshelves']) if book_data.get('bookshelves') else '',
                downloads=book_data['formats']['text/plain']['size'] if 'text/plain' in book_data.get('formats', {}) else 0
            )

    def filter_books(self, filter_criteria):
        queryset = Book.objects.all()
        criteria_list = filter_criteria.split(',')
        for criteria in criteria_list:
            if '=' in criteria:
                key, value = criteria.split('=')
                if key == 'author':
                    queryset = queryset.filter(author__icontains=value.strip())
                elif key == 'title':
                    queryset = queryset.filter(title__icontains=value.strip())
                elif key == 'language':
                    queryset = queryset.filter(language__icontains=value.strip())
                elif key == 'topic':
                    queryset = queryset.filter(subjects__icontains=value.strip()) | queryset.filter(bookshelves__icontains=value.strip())
        return queryset
