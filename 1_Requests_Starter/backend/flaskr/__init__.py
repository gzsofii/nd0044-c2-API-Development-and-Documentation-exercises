import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

def paginate_books(books, request):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * BOOKS_PER_SHELF
  end = start + BOOKS_PER_SHELF

  books = [book.format() for book in books]
  current_books = books[start:end]

  return current_books

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there. 
#     If you do not update the endpoints, the lab will not work - of no fault of your API code! 
#   - Make sure for each route that you're thinking through when to abort and with which kind of error 
#   - If you change any of the response body keys, make sure you update the frontend to correspond. 

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  # @TODO: Write a route that retrivies all books, paginated. 
  #         You can use the constant above to paginate by eight books.
  #         If you decide to change the number of books per page,
  #         update the frontend to handle additional books in the styling and pagination
  #         Response body keys: 'success', 'books' and 'total_books'
  # TEST: When completed, the webpage will display books including title, author, and rating shown as stars

  @app.route('/books')
  def get_books():
    books = Book.query.order_by(Book.id).all()
    current_books = paginate_books(books, request)
    total_books = len(books)

    if len(current_books) == 0:
      abort(404)
        
    resp = jsonify({
      "success": True,
      "books": current_books,
      "total_books": total_books
    })
    return resp
    

  # @TODO: Write a route that will update a single book's rating. 
  #         It should only be able to update the rating, not the entire representation
  #         and should follow API design principles regarding method and route.  
  #         Response body keys: 'success'
  # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh

  @app.route('/books/<int:book_id>', methods=["PATCH"])
  def update_rating(book_id):
    new_rating = request.get_json()['rating']

    try:
      book = Book.query.get(book_id)
      if book is None:
          print("no book with given id")
          abort(404)
      print('Old rating: ', book.rating)
      print('New rating: ', new_rating)
      book.rating = new_rating
      book.update()

      return jsonify({
      'success': True,
      'id': book_id
    })

    except:
      print("Something went wrong when updating book")
      abort(400)      
    


  # @TODO: Write a route that will delete a single book. 
  #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
  #        Response body keys: 'success', 'books' and 'total_books'

  # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.
  @app.route('/books/<int:book_id>', methods=["DELETE"])
  def delete_book(book_id):
    try:
      book = Book.query.get(book_id)

      if book is None:
        print('Book not found')
        abort(404)
      print('deleting book by ', book.author)
      book.delete()

      books = Book.query.order_by(Book.id).all()
      total_books = len(books)
      current_books = paginate_books(books, request)
      return jsonify({
        'succes': True,
        'deleted': book_id,
        'books': current_books,
        'total_books': total_books
      })
    except:
      print('Something went wrong when deleting')
      abort(422)

  # @TODO: Write a route that create a new book. 
  #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
  # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books. 
  #       Your new book should show up immediately after you submit it at the end of the page. 
  @app.route('/books', methods=["POST"])
  def create_book():
    new_book = request.get_json()
    
    try:
      book = Book(title=new_book['title'], author=new_book['author'], rating=new_book['rating'])
      book.insert()

      books = Book.query.order_by(Book.id).all()
      total_books = len(books)
      current_books = paginate_books(books, request)

      return jsonify({
        'success': True,
        'created': book.id,
        'books': current_books,
        'total_books': total_books
      })

    except:
      print("Something went wrong when creating new book")
      abort(422)
  return app

    