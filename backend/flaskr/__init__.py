import os
from flask import Flask, request, abort,json, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from werkzeug.exceptions import HTTPException
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def pagination(request, data, per_page = 10):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * per_page
  end = start + per_page
  items = [item.format() for item in data]
  return items[start:end]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources = {r"/":{"origins":"*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', "Content-Type, Authorization, true")
    response.headers.add('Access-Control-Allow-Methods', "GET,POST,DELETE,OPTIONS")
    return response

  '''
  @TODO: DONE
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/')
  @app.route('/categories')
  def categories():
    categories = Category.query.order_by(db.desc(Category.id)).all()
    if len(categories):
      return jsonify({
        "success": True,
        "categories":  {category.id:category.type for category in categories}
      })
    else:
      abort(404)



  '''
  @TODO: DONE
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route("/questions")
  def questions():
    '''
    This function gets all questions paginated based on the current page number
    Returns:
      - success value
      - paginated questions
      - categories
      - total number of questions
    '''
    try:
      all_questions = Question.query.order_by(db.desc(Question.id)).all() # Get all questions form the DB
      paginated_questions = pagination(request,all_questions, QUESTIONS_PER_PAGE) # paginate the questions
      all_categories = Category.query.order_by(db.desc(Category.id)).all() # Get all categories from the DB

      formatted_categories = {category.id:category.type for category in all_categories} # format the category to suit the frontend
      
      if len(paginated_questions) == 0:
        abort(404)

      else:
        return jsonify({
          "success":True,
          "questions":paginated_questions,
          "categories": formatted_categories,
          "total_questions":len(all_questions),
          "current_category":""
        })
    except Exception:
      abort(404)

  '''
  @TODO: DONE
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:question_id>", methods = ["DELETE"])
  def delete_question(question_id):
    '''
    This function deletes the question with the given ID if EXISTS 
    Returns:
      - success value
      - paginated questions
      - deleted question ID
      - total number of questions
    '''
    try:
      question = Question.query.get(question_id)
      if question is not None: # check the existance of the requested question
        question.delete()
      else:
        abort(422)

      questions = Question.query.order_by(db.desc(Question.id)).all()

      return jsonify({
        "success":True,
        "deleted": question_id,
        "questions":[question.format() for question in questions],
        "total_questions": len(questions)
      })
    except Exception:
      abort(422)

  '''
  @TODO: DONE
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions", methods = ["POST"])
  def create_question():
    '''
    This function adds new question using the submitted values:
      - question
      - answer
      - category
      - difficulty
    Returns:
      - success value
      - paginated questions
      - the inserted question
      - total number of questions
    '''
    data = request.get_json()
    # get wuestion data, using 'strip' to remove any leading or trailing spaces
    question_data = {"question": data['question'].strip(),
                  "answer": data['answer'].strip(),
                  "difficulty": data['difficulty'],
                  "category": data['category']
                  }

    # check if the question and answer both are not left empty
    if (question_data['answer'] != "") & (question_data['question'] != "") & (question_data['category'] is not None) & (question_data['difficulty'] is not None):
      try:
        new_question = Question(question = question_data['question'],
                                answer = question_data['answer'],
                                category = question_data['category'],
                                difficulty = question_data['difficulty'])
        new_question.insert()
        questions = Question.query.order_by(db.desc(Question.id)).all()
        paginated_questions = pagination(request, questions,QUESTIONS_PER_PAGE)
        return jsonify({
          "success": True,
          "questions": paginated_questions,
          "inserted_question": question_data,
          "total_questions": len(questions)
        })
      except Exception:
       abort(400)
    else:
      abort(400)

  '''
  @TODO: DONE
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route("/questions/search", methods = ['POST'])
  def search_questions():
    '''
    This function searches questions according to the given searchTerm and returns them paginated
    Returns:
      - success value
      - paginated questions
      - total number of questions
    '''
    try:
      data = request.get_json()
      search_term = data['searchTerm']

      questions = Question.query.filter(Question.question.ilike('%'+search_term+'%')).all()
      questions = pagination(request,questions,QUESTIONS_PER_PAGE)
      total_questions = Question.query.count()

      return jsonify({
        "success": True,
        "questions": questions,
        "total_questions": total_questions,
        "current_category": ""
      })

    except Exception:
      abort(500)


  '''
  @TODO: DONE
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<int:category_id>/questions")
  def get_category_questions(category_id):
    '''
    This function gets all questions within the given category and they are paginated based on the current page number
    Returns:
      - success value
      - paginated questions
      - total number of questions
      - current category
    '''
    try:
      category_type = Category.query.get(category_id).format()['type']
      questions = Question.query.filter(Question.category==category_id).all()
      formatted_questions = pagination(request,questions,QUESTIONS_PER_PAGE)

      if len(questions):

        return jsonify({
          "success": True,
          "questions": formatted_questions,
          "total_questions": len(questions),
          "current_category":category_type
        })

      else:
        abort(422)

    except Exception:
      abort(422)


  '''
  @TODO: DONE
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route("/quizzes", methods = ["POST"])
  def get_quizzes():
    '''
    This function gets a random question within the selected category that wasn't asked before in the same round
    Returns:
      - success value
      - random question from the DB
    '''
    try:
      data= request.get_json()
      # since the frontend returns the quiz_category as dict {"type":'click', 'id':1}
      if isinstance(data['quiz_category'], dict):
        category_type = data['quiz_category']['id']
      else: # to suit the request sent using the test script
        category_type = data['quiz_category']

      previous_questions = data['previous_questions']

      if category_type==0: # if the selected category was 'All', return all the questions
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      elif category_type: # else return the questions within the selected category
        questions = Question.query.filter(Question.category==category_type, Question.id.notin_(previous_questions)).all()
      
      if len(questions)==0: # if the category is not available
        abort(404)

      question = random.choice(questions).format()
      if question:
        return jsonify({
          "success":True,
          "question": question
        })


    except Exception:
      abort(404)



  '''
  @TODO: DONE
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(HTTPException)
  def handle_exception(e):
    '''
    This function is a generic exception handler
    Returns:
      - success value
      - error code
      - error message
      - error description
    '''
    # https://flask.palletsprojects.com/en/1.1.x/errorhandling/#generic-exception-handlers
    
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "success":False,
        "error": e.code,
        "message": e.name,
        "description": e.description,

    })
    response.content_type = "application/json"
    return response
  return app

    