<template>
  <div class="product-detail" v-if="ready_to_show">
    <!-- Product Information -->
    <div class="product-info">
      <h1 class="product-title">{{ product.product_name }}</h1>
      <p class="product-description">{{ product.product_description }}</p>
      <p class="product-price">Price: ${{ product.price.toFixed(2) }}</p>
    </div>

    <!-- Customer Reviews -->
    <div class="reviews-section">
      <h2>Customer Reviews</h2>
      <p v-if="reviews.length === 0">No reviews yet.</p>

      <!-- Review List -->
      <div v-for="(review, index) in reviews" :key="index" class="review-card">
        <div class="review-rating">
          <span v-if="review.rating !== null">
            <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= review.rating }">★</span>
          </span>
          <span v-else class="no-rating">No Rating</span>
        </div>
        <p class="review-comment" v-if="review.comment">{{ review.comment }}</p>
        <p class="no-comment" v-else>No comment provided.</p>

        <!-- Review Publish Time -->
        <p class="review-time">
          <strong>Published on:</strong> {{ formatDate(review.comment_time) }}
        </p>

        <!-- Merchant Reply -->
        <div class="review-reply" v-if="review.reply">
          <strong>Merchant Reply:</strong>
          <p>{{ review.reply }}</p>
          <p class="reply-time">
            <strong>Reply time:</strong> {{ formatDate(review.reply_time) }}
          </p>

          <!-- Add/Delete Reply Buttons (only if it's the seller's review) -->
          <div v-if="user_id === seller_id">
            <button @click="deleteReply(review.review_id)" class="del-reply-btn">Delete Reply</button>
          </div>
          
        </div>
        
        <!-- Add Reply Button (only if the user is the seller) -->
        <div v-if="user_id === seller_id && !review.reply">
          <button @click="toggleAddReply(review.review_id)" class="add-reply-btn">Add Reply</button>
        </div>

        <!-- Delete Review Button (only if it's the user's review) -->
        <button v-if="review.user_id === user_id && user_id !== seller_id"
          @click="deleteReview(review.review_id)">Delete Review</button>
      </div>

      <!-- Add Review Button -->
      <button v-if="!addReviewMode && user_id !== seller_id" @click="toggleAddReview" class="add-review-btn">Add Your
        Review</button>


      <!-- Add Review Form (Modal Style) -->
      <div v-if="addReviewMode" class="add-review-modal">
        <div class="modal-content">
          <h3>Add Your Review</h3>

          <form @submit.prevent="submitReview">
            <!-- Rating Selection -->
            <div class="form-group">
              <label for="rating">Rating:</label>
              <select v-model="newReview.rating" id="rating" class="form-control">
                <option v-for="n in 5" :key="n" :value="n">{{ n }} Star</option>
              </select>
            </div>

            <!-- Comment Input -->
            <div class="form-group">
              <label for="comment">Comment:</label>
              <textarea v-model="newReview.comment" id="comment" class="form-control"
                placeholder="Add your comment here..."></textarea>
            </div>

            <!-- Buttons -->
            <div class="form-buttons">
              <button type="submit" class="submit-btn">Submit</button>
              <button type="button" @click="toggleAddReview" class="cancel-btn">Cancel</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Add Reply Form (Modal Style) -->
      <div v-if="addReplyMode" class="add-reply-modal">
        <div class="modal-content">
          <h3>Add Your Reply</h3>

          <form @submit.prevent="submitReply">

            <!-- Comment Input -->
            <div class="form-group">
              <label for="reply">Reply:</label>
              <textarea v-model="newReply.reply" id="reply" class="form-control"
                placeholder="Add your reply here..."></textarea>
            </div>

            <!-- Buttons -->
            <div class="form-buttons">
              <button type="submit" class="submit-btn">Submit</button>
              <button type="button" @click="toggleAddReply" class="cancel-btn">Cancel</button>
            </div>
          </form>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      product: {},
      reviews: [],
      ready_to_show: false,
      addReviewMode: false, // Control to show/hide add review form
      newReview: {
        rating: null,
        comment: '',
      },
      addReplyMode: false, // Control to show/hide add reply form
      newReply: {
        reply: '',
      },
      seller_id: null, // Seller ID of the product
    };
  },
  async mounted() {
    await this.getProduct();
  },
  props: {
    user_id: { type: Number, required: true },
    product_id: { type: Number, required: true },
  },
  methods: {
    async getProduct() {
      try {
        const response = await axios.get(`http://localhost:5000/product/${this.product_id}`);
        this.product = response.data["product"];
        this.reviews = response.data["reviews"];
        this.seller_id = response.data["seller_id"];
        this.ready_to_show = true;
      } catch (error) {
        console.log(error);
      }
    },

    // Format date to a readable format
    formatDate(date) {
      const d = new Date(date);
      return d.toLocaleString();
    },

    // Toggle the visibility of the "Add Review" form
    toggleAddReview() {
      this.addReviewMode = !this.addReviewMode;
    },

    // Submit a new review
    async submitReview() {
      try {
        this.newReview.user_id = this.user_id;
        this.newReview.product_id = this.product_id;
        const response = await axios.post(`http://localhost:5000/review/0`, this.newReview);
      } catch (error) {
        alert('Failed to add review');
        console.error(error);
      }
      this.newReview = {}
      this.newReview.rating = null;
      this.newReview.comment = '';
      this.addReviewMode = false; // Hide the form after submission
      this.getProduct(); // Reload the product page to show the new review
    },

    // Delete a review
    async deleteReview(review_id) {
      try {
        const response = await axios.get(`http://localhost:5000/review/${review_id}`);
      } catch (error) {
        alert('Failed to delete review');
        console.error(error);
      }
      this.getProduct(); // Reload the product page to show the deleted review
    },

    // Toggle Add Reply for a review
    toggleAddReply(review_id) {
      this.selectedReviewId = review_id;
      this.addReplyMode = !this.addReplyMode;
      this.newReply.reply = '';
    },

    // Submit a reply to a review
    async submitReply() {
      try {
        this.newReply.review_id = this.selectedReviewId;
        const response = await axios.post(`http://localhost:5000/reply/0`, this.newReply);
      } catch (error) {
        alert('Failed to add reply');
        console.error(error);
      }
      this.addReplyMode = false; // Hide the form after submission
      this.selectedReviewId = null;
      this.newReply.reply = '';
      this.getProduct(); // Reload to show the new reply
    },

    // Delete a reply
    async deleteReply(review_id) {
      try {
        const response = await axios.get(`http://localhost:5000/reply/${review_id}`);
      } catch (error) {
        alert('Failed to delete reply');
        console.error(error);
      }
      this.getProduct(); // Reload the product page to show the deleted reply
    },

    debug(id){
      console.log(id);
      console.log(this.seller_id);
      console.log(this.user_id);
      console.log(this.product_id);
    }

  },
};
</script>

<style scoped>
.product-detail {
  max-width: 700px;
  margin: 30px auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.product-info {
  margin-bottom: 40px;
}

.product-title {
  font-size: 2rem;
  color: #222;
  margin-bottom: 10px;
}

.product-description {
  font-size: 1rem;
  color: #555;
}

.product-price {
  font-size: 1.2rem;
  font-weight: bold;
  margin-top: 10px;
  color: #0a7cff;
}

.reviews-section {
  margin-top: 40px;
}

.review-card {
  background: #f8f9fa;
  border-left: 5px solid #0a7cff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  transition: background 0.3s;
}

.review-card:hover {
  background: #e9f5ff;
}

.review-rating {
  margin-bottom: 8px;
  font-size: 1.1rem;
}

.star {
  color: #ddd;
  font-size: 1.3rem;
  margin-right: 2px;
}

.star.filled {
  color: #ffc107;
}

.no-rating {
  color: #999;
  font-style: italic;
}

.review-comment,
.no-comment {
  font-size: 1rem;
  color: #333;
  margin-bottom: 8px;
}

.no-comment {
  font-style: italic;
  color: #888;
}

.review-reply {
  margin-top: 10px;
  padding-left: 10px;
  border-left: 3px solid #aaa;
  color: #444;
  font-size: 0.95rem;
}

.review-time,
.reply-time {
  font-size: 0.9em;
  color: #888;
}


/* Add Review Button */
.add-review-btn {
  background-color: #0a7cff;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s ease;
}

.add-review-btn:hover {
  background-color: #005bb5;
}

/* Modal Style for Add Review Form */
.add-review-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  /* Overlay */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.add-review-modal .modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 400px;
}

h3 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

label {
  font-size: 16px;
  color: #333;
  display: block;
  margin-bottom: 8px;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

textarea.form-control {
  height: 100px;
  resize: vertical;
}

.form-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.submit-btn,
.cancel-btn {
  padding: 10px 20px;
  font-size: 16px;
  border-radius: 5px;
  cursor: pointer;
  border: none;
}

.submit-btn {
  background-color: #28a745;
  color: white;
}

.submit-btn:hover {
  background-color: #218838;
}

.cancel-btn {
  background-color: #dc3545;
  color: white;
}

.cancel-btn:hover {
  background-color: #c82333;
}

/* Modal Background */
.add-reply-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  transition: opacity 0.3s ease, visibility 0.3s ease;
}

.add-reply-modal .modal-content {
  background-color: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  width: 450px;
  max-width: 100%;
  transform: translateY(-50px);
  animation: modal-appear 0.4s forwards;
}

/* Modal Content Animation */
@keyframes modal-appear {
  from {
    opacity: 0;
    transform: translateY(-50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Close on Click Outside */
.add-reply-modal .modal-content {
  animation: modal-slide-up 0.5s ease;
}

@keyframes modal-slide-up {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Add Reply Button */
.add-reply-btn {
  background-color: #0a7cff;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s ease;
}

.add-reply-btn:hover {
  background-color: #005bb5;
}

/* Add Reply Button */
.del-reply-btn {
  background-color: #60ed4d;
  color: white;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s ease;
}

.del-reply-btn:hover {
  background-color: #137844;
}

</style>
