<template>
  <router-view></router-view>
</template>

<script>
import homepage from './components/homepage.vue'
import my_purchase from './components/my_purchase.vue'
import searchbar from './components/searchbar.vue'
import login from './components/login.vue'

export default {
  name: 'App',
  components: {
    homepage,
    my_purchase,
    searchbar,
    login
  }
}
</script>
