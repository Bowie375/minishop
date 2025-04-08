from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

from minishop.database.orm import Database


class Server:
    def __init__(self, db_url='data/test.db'):
        self.db = Database(db_url)
        self.app = Flask(__name__)
        self.api = Api(self.app)

        # Enable CORS
        CORS(self.app)

    class login(Resource):
        def __init__(self, db: Database):
            self.db = db

        def post(self):
            data = request.json
            username = data['username']
            password_hash = data['password_hash']
            user_id = self.db.confirm_user(username, password_hash)
            if user_id is not None:
                return {"user_id": user_id}, 200
            else:
                return {"error": "Invalid username or password"}, 401

    class search(Resource):
        def __init__(self, db: Database):
            self.db = db

        def post(self):
            data = request.json
            query = data['query']
            field = data['field']
            results = self.db.search_for_product(query, field)
            return results, 200

    class profile(Resource):
        def __init__(self, db: Database):
            self.db = db
        
        def get(self, user_id):
            """Retrieve user profile"""
            user = self.db.get_user(user_id)
            if user is not None:
                return user, 200
            else:
                return {"error": "User not found"}, 404

        def post(self, user_id):
            """Update user profile"""
            user = self.db.update_user(user_id, **request.json)
            if user:
                return True, 200
            else:
                return {"error": "User not found"}, 404

    class purchase(Resource):
        def __init__(self, db: Database):
            self.db = db

        def get(self, user_id):
            """Retrieve user purchase history"""
            orders, trackings = self.db.get_purchase_history(user_id)
            if orders:
                return {"orders": orders, "trackings": trackings}, 200
            else:
                return {"error": "No purchase history found"}, 404

    class product(Resource):
        def __init__(self, db: Database):
            self.db = db

        def get(self, product_id):
            """Retrieve product details"""
            product, reviews, seller_id = self.db.get_product(product_id)
            if product is not None:
                return {"product": product, "reviews": reviews, 
                        "seller_id": seller_id}, 200
            else:
                return {"error": "Product not found"}, 404

    class review(Resource):
        def __init__(self, db: Database):
            self.db = db

        def get(self, review_id):
            """Delete review"""
            success = self.db.delete_review(review_id)
            if success:
                return True, 200
            else:
                return {"error": "Review not found"}, 404

        def post(self, review_id):
            """Create new review"""
            review = request.json
            success = self.db.add_review(review)
            if success:
                return True, 200
            else:
                return {"error": "Failed to add review"}, 400

    class reply(Resource):
        def __init__(self, db: Database):
            self.db = db

        def get(self, review_id):
            """Delete reply"""
            success = self.db.delete_reply(review_id)
            if success:
                return True, 200
            else:
                return {"error": "Review not found"}, 404

        def post(self, review_id):
            """Create new review"""
            reply = request.json
            success = self.db.add_reply(reply)
            if success:
                return True, 200
            else:
                return {"error": "Failed to add review"}, 400

    #class UserList(Resource):
    #    def get(self):
    #        """Retrieve all users"""
    #        return users

    #    def post(self):
    #        """Create new user"""
    #        new_id = max(users.keys()) + 1
    #        data = request.json
    #        users[new_id] = {"name": data["name"], "email": data["email"]}
    #        return users[new_id], 201

    def run(self, host="127.0.0.1", port=5000):
        # Registering resources with API
        self.api.add_resource(self.login, "/login", 
                              resource_class_args=[self.db])
        self.api.add_resource(self.search, "/search", 
                              resource_class_args=[self.db])
        self.api.add_resource(self.profile, "/profile/<int:user_id>", 
                              resource_class_args=[self.db])
        self.api.add_resource(self.purchase, "/purchase/<int:user_id>", 
                              resource_class_args=[self.db])
        self.api.add_resource(self.product, "/product/<int:product_id>", 
                              resource_class_args=[self.db])
        self.api.add_resource(self.review, "/review/<int:review_id>", 
                              resource_class_args=[self.db])
        self.api.add_resource(self.reply, "/reply/<int:review_id>", 
                              resource_class_args=[self.db])
        #self.api.add_resource(self.UserList, "/users")
        self.app.run(host=host, port=port)


if __name__ == "__main__":
    server = Server("../data/e_commerce.db")
    server.run()