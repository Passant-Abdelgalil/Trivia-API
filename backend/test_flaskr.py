import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

def pagination( data, per_page=10):
    page = 1
    start = (page - 1) * per_page
    end = start + per_page
    items = [item.format() for item in data]
    return items[start:end]


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        password = "postgres"
        username = 'postgres'
        url = 'localhost:5432'
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            username, password, url, self.database_name)
        setup_db(self.app, self.database_path)

        self.question = "What is your name?"
        self.answer = "passant"
        self.category = 1
        self.difficulty = 1

        self.new_question = {
            "question": "What is your name?",
            "answer": "passant",
            "difficulty": 1,
            "category": 1
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass


    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        '''
        This function test the success of retrieving all questions paginated based on the current page number
        Assuers:
        - success value
        - paginated questions
        - categories
        - total number of questions
        - format of the retrieved questions
        '''
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        # request the questions route
        res = self.client().get('/questions')
        data = json.loads(res.data)
        # check the success of the request
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # check there are questions to retrieve
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_questions'])
        # check the format of the retrieved questions
        self.assertTrue(data['questions'][0]['question'])
        self.assertTrue(data['questions'][0]['answer'])
        self.assertTrue(data['questions'][0]['difficulty'])
        self.assertTrue(data['questions'][0]['category'])

    def test_404_sent_request_beyond_valid_page(self):
        '''
        This function tests handling error when requesting a not valid page
        Assuers:
        - success value
        - status code
        - error message
        '''
        res = self.client().get("/questions?page=10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not Found")

    def test_get_unknownRoute(self):
        '''
        This function tests handling error when requesting non available route
        Assuers:
            - success value
            - status code
            - error message
        '''
        # request unavailable route
        res = self.client().get("/questoins")
        data = json.loads(res.data)
        # check the request response is 404
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not Found")

    def test_add_newQuestion(self):
        '''
        This function test the success of adding new question using the submitted variables
        Assuers:
        - success value
        - paginated questions
        - the validity of the submitted question values
        - total number of questions
        - format of the question
        - success of insertion in the database
        '''
        # 1) Case: valid data
        # post request to add the question
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        # check the success of the request
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        # check the values of the validity of the inserted question
        self.assertEqual(data['inserted_question']['question'], self.question)
        self.assertEqual(data['inserted_question']['answer'], self.answer)
        self.assertEqual(data['inserted_question']
                         ['difficulty'], self.difficulty)
        self.assertEqual(data['inserted_question']['category'], self.category)
        # check the question was inserted correctly in the database
        inserted_question = Question.query.order_by(
            self.db.desc(Question.id)).first().format()
        self.assertTrue(inserted_question)
        self.assertEqual(inserted_question['answer'], self.answer)
        self.assertEqual(inserted_question['question'], self.question)
        self.assertEqual(inserted_question['difficulty'], self.difficulty)
        self.assertEqual(inserted_question['category'], self.category)

    def test_add_corrupted_question(self):
        '''
        This function tests handling error when trying to add new question using the submitted variables
        that are not valid
        Assuers:
        - success value
        - missing question value
        - missing answer value
        - missing category value
        - missing difficulty value
        - status code
        - error message
        '''
        error_message = "Bad Request"
        route = "/questions"
        # 2) Case: Missing question value
        self.new_question['question'] = ""

        res = self.client().post(route, json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], error_message)

        # 3) Case: Missing Answer
        self.new_question['question'] = self.question
        self.new_question['answer'] = ""

        res = self.client().post(route, json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], error_message)

        # Next two cases are redundant since category and difficulty both should have
        # default values from the drop-down list, but in case something went wrong!

        # 4) Case: Missing Category
        self.new_question['answer'] = self.answer
        self.new_question['category'] = None

        res = self.client().post(route, json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], error_message)

        # 5) Case: Missing Difficulty
        self.new_question['category'] = self.category
        self.new_question['difficulty'] = None

        res = self.client().post(route, json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], error_message)

        self.new_question['difficulty'] = self.difficulty

    def test_delete_question(self):
        '''
        This function test the success of deleting a question with the given ID
        Assuers:
        - success value
        - paginated questions
        - the existance of the requested question
        - total number of questions
        - format of the question
        - success of deletion in the database
        '''
        res = self.client().delete("/questions/5")
        data = json.loads(res.data)
        deleted_question = Question.query.filter(
            Question.id == 5).one_or_none()
        # check the success of the request
        self.assertTrue(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 5)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        # check the format of the retrieved questions
        self.assertTrue(data['questions'][0]['question'])
        self.assertTrue(data['questions'][0]['answer'])
        self.assertTrue(data['questions'][0]['difficulty'])
        self.assertTrue(data['questions'][0]['category'])
        # check the success of deletion from the database
        self.assertFalse(deleted_question)

    def test_422_delete_unavailable_question(self):
        '''
        This function tests handling error when trying to delete a question that does not exist!
        Assuers:
        - success value
        - status code
        - error message
        '''
        res = self.client().delete("/questions/10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable Entity")

    def test_search_question(self):
        '''
        This function test the success of searching a question based on the given searchTerm
        Assuers:
        - success value
        - returned list of questions
        - total number of questions
        '''
        res = self.client().post("/questions/search",
                                 json={"searchTerm": "title"})
        data = json.loads(res.data)
        questions = Question.query.filter(
                Question.question.ilike('%title%')).all()
        questions = pagination(questions)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), len(questions))
        self.assertTrue(data['total_questions'])
        
    def test_search_question_with_nonsense_searchTerm(self):
        '''
        This function test the success of searching a question with a searchTerm that doesn't exist
        Assuers:
        - success value
        - empty list of returned questions
        - total number of questions
        '''
        res = self.client().post("/questions/search",
                                 json={"searchTerm": "dfsghj"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']),0)
        self.assertTrue(data['total_questions'])

    def test_get_category_questions(self):
        '''
        This function test the success of retrieving questions within the given category
        Assuers:
        - success value
        - paginated questions
        - current category
        - total number of questions
        '''
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        current_category = Category.query.get(1).format()['type']

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], current_category)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_422_get_unavailable_category_questions(self):
        '''
        This function tests handling error when trying to retrieve questions within unavailable category
        Assuers:
        - success value
        - status code
        - error message
        '''
        res = self.client().get("/categories/100/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable Entity")

    def test_get_quizzes(self):
        '''
        This function test the success of retrieving a random question based on the given category type
        and previoud questions
        Assuers:
        - success value
        - paginated questions
        - current category
        - total number of questions
        '''
        previous_questions = [1, 2]
        res = self.client().post(
            "/quizzes", json={"quiz_category": 1, "previous_questions": previous_questions})
        data = json.loads(res.data)

        # check the success of the request
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['id'] not in previous_questions)
        # check the format of the retrieved question
        self.assertTrue(data['question']['question'])
        self.assertTrue(data['question']['answer'])
        self.assertTrue(data['question']['difficulty'])
        self.assertTrue(data['question']['category'])

    def test_404_faliure_getting_quizzes(self):
        '''
        This function tests handling error when retrieving a random question based within non available category
        Assuers:
        - success value
        - error status code
        - error message
        '''
        res = self.client().post(
            "/quizzes", json={"quiz_category": "nonsense", "previous_questions": []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not Found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
