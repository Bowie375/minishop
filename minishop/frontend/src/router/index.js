import { createRouter, createWebHistory } from "vue-router";

// Import the components
import login from "../components/login.vue";
import searchbar from "../components/searchbar.vue";
import my_purchase from "../components/my_purchase.vue";
import product from "../components/product.vue";

// Define the routes
const routes = [
  {
    path: "/",
    component: login,
  },
  {
    path: "/components/searchbar",
    component: searchbar,
  },
  {
    path: "/components/searchbar",
    component: searchbar,
  },
  {
    path: "/components/my_purchase",
    component: my_purchase,
  },
  {
    path: "/components/product/:product_id",
    component: product,
    props: true,
  },
];

// Create the router instance
const router = createRouter({
  history: createWebHistory(), // Enables history mode (clean URLs without hashes)
  routes,
});

export default router;
