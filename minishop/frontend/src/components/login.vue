<template>
    <div v-if="login_status === false" class="login-form">
      <h1>Login</h1>
      <form @submit.prevent="login">
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="username" required>
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" required>
        <button type="submit">Login</button>
      </form>
    </div>
    <div v-else-if="login_status === true">
      <div class="top-bar">
        <button class="nav-button" @click="currentModule = 'searchbar'">首页</button>
        <button class="nav-button" @click="currentModule = 'homepage'">我的</button>
        <button class="nav-button" @click="currentModule = 'my_purchase'">购物记录</button>
      </div>
  
      <div class="content-area">
        <component :is="currentModule" :user_id="user_id" 
        @childShowProduct="handleChildShowProduct" :product_id="show_product_id"/>
      </div>
    </div>
  </template>
  
  <script>
  import homepage from './homepage.vue'
  import my_purchase from './my_purchase.vue'
  import searchbar from './searchbar.vue'
  import product from './product.vue';
  import CryptoJS from 'crypto-js';
  import axios from 'axios';

  export default {
    components: {
      homepage,
      my_purchase,
      searchbar,
      product
    },
    data() {
      return {
        login_status: false,
        username: '',
        password: '',
        user_id: null,
        show_product_id: null,
        currentModule: 'searchbar'  // default module shown
      }
    },
    methods: {
      login() {
        let password_hash = CryptoJS.SHA256(this.password).toString(CryptoJS.enc.HEX)
        axios.post('http://localhost:5000/login', {
          username: this.username,
          password_hash: password_hash
        }).then(res => {
          console.log('Login success:', res.data)
          this.login_status = true
          this.user_id = res.data.user_id
        }).catch(err => {
          alert('Login failed!')
          console.error(err)
        })
      },
      handleChildShowProduct(data) {
        this.currentModule = "product"
        this.show_product_id = data
      }
    }
  }
  </script>
  
  <style>
  /* General styling */
  .login-form {
    background-color: #f7f7f7;
    border-radius: 10px;
    padding: 30px;
    max-width: 400px;
    margin: auto;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    font-family: 'Arial', sans-serif;
  }
  
  /* Title styling */
  .login-form h1 {
    text-align: center;
    font-size: 24px;
    margin-bottom: 20px;
    color: #333;
  }
  
  /* Label styling */
  .login-form label {
    display: block;
    font-size: 14px;
    color: #555;
    margin-bottom: 5px;
  }
  
  /* Input field styling */
  .login-form input[type="text"],
  .login-form input[type="password"] {
    width: 100%;
    padding: 12px;
    margin-bottom: 15px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-size: 16px;
    color: #333;
    transition: border-color 0.3s ease-in-out;
  }
  
  /* Input focus effect */
  .login-form input[type="text"]:focus,
  .login-form input[type="password"]:focus {
    border-color: #5c8dff;
    outline: none;
  }
  
  /* Button styling */
  .login-form button {
    width: 100%;
    padding: 12px;
    background-color: #5c8dff;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  /* Button hover effect */
  .login-form button:hover {
    background-color: #4a76d0;
  }
  
  /* Button active effect */
  .login-form button:active {
    background-color: #4068b0;
  }
  
  /* Fancy Top Bar */
  .top-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #2c3e50;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  /* Button Style */
  .nav-button {
    background-color: #3498db;
    color: white;
    font-size: 16px;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
    margin: 0 10px;
  }
  
  .nav-button:hover {
    background-color: #2980b9;
    transform: scale(1.05);
  }
  
  .nav-button:focus {
    outline: none;
  }
  
  /* Content Area Styling */
  .content-area {
    margin: 20px;
    padding: 20px;
    background-color: #f4f6f7;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  </style>
  