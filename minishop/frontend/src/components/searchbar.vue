<template>
  <div>
    <div class="search-container">
      <input v-model="searchQuery" type="text" placeholder="Search..." @input="onSearch" class="search-bar" />
      <select v-model="searchField" class="search-select">
        <option value="name">Name</option>
        <option value="description">Description</option>
        <option value="category">Category</option>
      </select>
    </div>

    <div v-if="searchResults.length > 0" class="search-results">
      <ul>
        <li v-for="(result, index) in searchResults" :key="index" @click="showProduct(result.product_id)">
          {{ result.product_name }}, {{ result.price }}
        </li>
      </ul>
    </div>
    <div v-else-if="searchQuery" class="no-results">
      No results found for "{{ searchQuery }}" in "{{ searchField }}" field.
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      searchQuery: '',
      searchField: 'name', // Default field to search in
      searchResults: []
    };
  },
  methods: {
    onSearch() {
      if (this.searchQuery) {
        axios.post('http://localhost:5000/search', {
          query : this.searchQuery,
          field : this.searchField
        }).then(res => {
          console.log('Search success:', res.data)
          this.searchResults = res.data;
        }).catch(err => {
          alert('Search failed!')
          console.error(err)
          this.searchResults = [];
        })
      } else {
        this.searchResults = [];
      }
    },
    showProduct(product) {
      this.$emit('childShowProduct', product);
    }
  }
};
</script>

<style scoped>
.search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-bar {
  width: 300px;
  padding: 8px;
  border: 1px solid #ccc;
}

.search-select {
  padding: 8px;
  border: 1px solid #ccc;
}

.search-results {
  margin: 20px;
  font-family: Arial, sans-serif;
}

.search-results ul {
  padding-left: 0;
}

.search-results li {
  text-decoration: underline;
  color: #007BFF;
  font-size: 16px;
  font-weight: 500;
  transition: color 0.3s ease, border-bottom 0.3s ease;
  padding-bottom: 2px;
  /* Add padding at the bottom to create space for the underline */
  border-bottom: 2px solid transparent;
  /* Invisible underline initially */
}

.search-results li:hover {
  color: #0056b3;
  /* Darker blue color on hover */
}

.search-results li:focus {
  outline: none;
  border-bottom: 2px solid #0056b3;
  /* Keeps the underline even when focused */
}

.no-results {
  color: red;
}
</style>