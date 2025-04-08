<template>
    <div class="purchase-history">
      <h2>购物记录</h2>
      <p v-if="purchases.length === 0">暂无记录</p>
      <ul class="history-list">
        <li v-for="(purchase, index) in purchases" :key="index" class="history-item">
          <div class="history-header">
            <span class="toggle-icon" @click="toggleTrack(index)">
              {{ purchase.showTrack ? '▼' : '▶' }}
            </span>
            <span class="product-name" @click="goToProduct(purchase[4])">
              {{ purchase[3] }}
            </span>
            — {{purchase[2]}} - {{purchase[5]}} x ¥{{purchase[6]}} - {{purchase[1]}}
          </div>
          <ul v-if="showTrack[index]" class="track-list">
            <li v-for="(step, i) in trackings[index]" :key="i" class="track-step">
              {{step[1]["status"]}} - {{ step[1]["location"] }} - {{ step[1]["timestamp"] }} - {{ step[0]["carrier"] }} - {{ step[0]["estimated_arrival"] }}
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </template>
  
<script>
import axios from 'axios'

export default {
    props: {
        user_id: { type: Number, required: true }
    },
    mounted() {
      axios.get('http://localhost:5000/purchase/' + this.user_id)
       .then(response => {
          this.purchases = response.data["orders"];
          this.trackings = response.data["trackings"];
          console.log(this.trackings);
          console.log(this.purchases);
        })
       .catch(error => {
          console.log(error);
        });
      this.showTrack = new Array(this.purchases.length).fill(false);
    },
    data() {
      return {
        purchases: [],
        trackings: [],
        showTrack: [],
      };
    },
    methods: {
      toggleTrack(index) {
        this.showTrack[index] = !this.showTrack[index];
      },
      goToProduct(productId) {
        this.$emit('childShowProduct', productId);
      }
    }
  };
  </script>
  
  <style scoped>
  .purchase-history {
    max-width: 600px;
    margin: 0 auto;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  
  .history-list {
    list-style: none;
    padding: 0;
    text-align: left;
  }
  
  .history-item {
    border-bottom: 1px solid #ddd;
    padding: 10px 0;
  }
  
  .history-header {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
  }
  
  .toggle-icon {
    font-weight: bold;
    cursor: pointer;
    user-select: none;
    width: 20px;
  }
  
  .product-name {
    color: #007bff;
    text-decoration: underline;
    cursor: pointer;
  }
  
  .track-list {
    margin-left: 30px;
    margin-top: 5px;
    padding-left: 10px;
    list-style-type: circle;
    color: #555;
  }
  
  .track-step {
    margin-bottom: 3px;
  }
  </style>
  