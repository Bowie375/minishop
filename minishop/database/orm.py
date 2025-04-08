from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from decimal import Decimal

from minishop.database.entities import *

def serialize(l : list):
    for i in range(len(l)):
        if isinstance(l[i], datetime):
            l[i] = l[i].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(l[i], Decimal):
            l[i] = float(l[i])
    return l


class Database:
    def __init__(self, db_url='data/test.db'):
        engine = create_engine(f'sqlite:///{db_url}')
        Session = sessionmaker(bind=engine)
        self.session = Session()
        print("[INFO]database constructed")

    def confirm_user(self, username, password_hash):
        user = self.session.query(User).filter_by(
            username=username, password_hash=password_hash).first()
        if user:
            return user.user_id
        else:
            return None
    
    def search_for_product(self, query, field):
        if field == 'name':
            products = self.session.query(Product).filter(Product.product_name.like(f'%{query}%')).all()
        elif field == 'category':
            products = self.session.query(Product)\
            .join(Product_Tag, Product.product_id == Product_Tag.product_id)\
            .join(Category, Product_Tag.category_id == Category.category_id)\
            .filter(Category.category_name.like(f'%{query}%')).all()
        elif field == 'description':
            products = self.session.query(Product).filter(Product.product_description.like(f'%{query}%')).all()
        else:
            products = []
        return [product.to_dict() for product in products]

    def get_user(self, user_id):
        user = self.session.query(
            User.username, User.email, User.phone_number, User.address)\
            .filter_by(user_id=user_id).first()
        if user:
            user_serialized = serialize(user)
            return {'username': user_serialized[0], 'email': user_serialized[1], 'phone_number': user_serialized[2], 'address': user_serialized[3]}
        else:
            return None
        
    def update_user(self, user_id, **kwargs):
        try:
            # Step 1: Query for the user by user_id
            user = self.session.query(User).filter_by(user_id=user_id).first()

            if user:
                # Step 2: Update the user's information
                user.username = kwargs.get('username', user.username)
                user.email = kwargs.get('email', user.email)
                user.phone_number = kwargs.get('phone_number', user.phone_number)
                user.address = kwargs.get('address', user.address)

                # Step 3: Commit the transaction to save changes
                self.session.commit()
                print(f"User {user_id} updated successfully!")
                return True
            else:
                print(f"User with id {user_id} not found.")

        except IntegrityError as e:
            # Step 4: Handle conflicts (like unique constraint violation)
            session.rollback()  # Rollback the transaction in case of error
            print(f"Error updating user: {e.orig}")  # Print error message

        except Exception as e:
            # Handle other exceptions
            session.rollback()
            print(f"An unexpected error occurred: {e}")
        return False

    def get_purchase_history(self, user_id):
        orders = self.session.query(
                Order_Table.order_id, Order_Table.order_status, Order_Table.created_at, 
                Product.product_name, Product.product_id, Order_Item.quantity, Order_Item.price_at_purchase,
                )\
               .join(Order_Item, Order_Table.order_id == Order_Item.order_id)\
               .join(Product, Order_Item.product_id == Product.product_id)\
               .filter(Order_Table.buyer_id == user_id).all()

        trackings = []
        for order in orders:
            tracking = self.session.query(Shipping, Shipping_Track)\
               .filter(Shipping.order_id == order[0])\
               .filter(Shipping_Track.shipping_id == Shipping.shipping_id).all()
            trackings.append([[t[0].to_dict(), t[1].to_dict()] for t in tracking])

        return [serialize(list(order)) for order in orders], trackings

    def get_product(self, product_id):
        product = self.session.query(Product).filter(Product.product_id == product_id).first()
        reviews = self.session.query(Review).filter(Review.product_id == product_id).all()
        seller_id = self.session.query(User.user_id)\
            .join(Store, User.user_id == Store.owner_id)\
            .join(Product, Store.store_id == Product.store_id)\
            .filter(Product.product_id == product_id).first()

        return product.to_dict(), [review.to_dict() for review in reviews], int(seller_id[0])

    def add_review(self, review):
        try:
            new_review = Review(
                user_id=review['user_id'],
                product_id=review['product_id'],
                comment=review['comment'],
                rating=review['rating'],
                comment_time=datetime.now(),
                reply=None,
                reply_time=None
            )
            self.session.add(new_review)
            self.session.commit()
            print(f"Review added successfully!")
            return True
        except IntegrityError as e:
            # Step 4: Handle conflicts (like unique constraint violation)
            session.rollback()  # Rollback the transaction in case of error
            print(f"Error adding review: {e.orig}")  # Print error message

        except Exception as e:
            # Handle other exceptions
            session.rollback()
            print(f"An unexpected error occurred: {e}")
        return False

    def delete_review(self, review_id):
        try:
            review = self.session.query(Review).filter_by(review_id=review_id).first()
            if review:
                self.session.delete(review)
                self.session.commit()
                print(f"Review {review_id} deleted successfully!")
                return True
            else:
                print(f"Review with id {review_id} not found.")
        except Exception as e:
            session.rollback()
            print(f"An unexpected error occurred: {e}")
        return False

    def add_reply(self, reply):
        try:
            review_id = reply["review_id"]
            review = self.session.query(Review).filter_by(review_id=review_id).first()
            if review:
                review.reply = reply["reply"]
                review.reply_time = datetime.now()
                self.session.commit()
                print(f"Reply for review {review_id} added successfully!")
                return True
            else:
                print(f"Review with id {review_id} not found.")
        except Exception as e:
            session.rollback()
            print(f"An unexpected error occurred: {e}")
        return False        

    def delete_reply(self, review_id):
        try:
            review = self.session.query(Review).filter_by(review_id=review_id).first()
            if review:
                review.reply = None
                review.reply_time = None
                self.session.commit()
                print(f"Reply for review {review_id} deleted successfully!")
                return True
            else:
                print(f"Review with id {review_id} not found.")
        except Exception as e:
            session.rollback()
            print(f"An unexpected error occurred: {e}")
        return False

    def excute_sql(self, sql):
        self.session.execute(sql)

    def __del__(self):
        self.session.close()

if __name__ == '__main__':
    db = Database("../data/e_commerce.db")
    session = db.session

    product_id = 1
    product = session.query(Product).filter(Product.product_id == product_id).first()
    reviews = session.query(Review).filter(Review.product_id == product_id).all()
    seller_id = session.query(User.user_id)\
        .join(Store, User.user_id == Store.owner_id)\
        .join(Product, Store.store_id == Product.store_id)\
        .filter(Product.product_id == product_id).first()

    print(product.to_dict(), [review.to_dict() for review in reviews], int(seller_id[0]))
    print(type(int(seller_id[0])))

