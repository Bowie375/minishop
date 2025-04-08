<template>
  <div class="user-profile-editor">
    <h2>User Profile</h2>

    <table class="user-info-table">
      <tr v-for="(value, key) in editableUser" :key="key">
        <td class="field-label">{{ key }}</td>
        <td @click="editField = key" class="field-value">
          <template v-if="editField === key">
            <input v-model="editableUser[key]" />
          </template>
          <template v-else-if="value !== null">
            {{ userData[key] }}
          </template>
          <template v-else> {{ "N/A" }} </template>
        </td>
      </tr>
    </table>

    <div v-if="errorMessage" class="error-message" ref="errorMsg">{{ errorMessage }}</div>
    <div v-else-if="editSuccess" class="success-message" ref="successMsg">Profile updated successfully.</div>

    <button @click="update" class="update-button">Update</button>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'homepage',
  props: {
    user_id: { type: Number, required: true }
  },
  data() {
    return {
      userData: {},
      editableUser: {},
      editField: null,
      editSuccess: false,
      errorMessage: '',
    }
  },
  async mounted() {
    try {
      let res = await axios.get(`http://localhost:5000/profile/${this.user_id}`)
      console.log('Load user profile success:', res.data)
      this.userData = res.data
      this.editableUser = { ...this.userData } // Clone user data for editing
    }
    catch (err) {
      alert('Load user profile failed!')
      console.error(err)
      this.userData = {}
    }
    window.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    window.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    formatKey(key) {
      console.log('Format key:', key)
      return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },
    async update() {
      this.errorMessage = ''
      try {
        // Simulate an API call
        this.editSuccess = await this.updateUserInfo(this.editableUser)
        console.log('Edit success:', this.editSuccess)
        if (!this.editSuccess) {
          this.editableUser = { ...this.userData } // Rollback change
          this.errorMessage = 'Update failed: duplicate or invalid information.'
        } else {
          this.userData = { ...this.editableUser } // Commit change
          this.editField = null
        }
      } catch (err) {
        this.errorMessage = 'An error occurred during update.'
      }
    },
    async updateUserInfo(newData) {
      try {
        const res = await axios.post(`http://localhost:5000/profile/${this.user_id}`, newData);
        console.log('Update user profile success:', res.data);
        return true;  // return true if successful
      } catch (err) {
        console.error('Update user profile failed:', err);
        return false; // return false if error
      }
    },
    handleClickOutside(event) {
      const errorMsgEl = this.$refs.errorMsg;
      if (errorMsgEl && !errorMsgEl.contains(event.target)) {
        this.errorMessage = ''
      }
      const successMsgEl = this.$refs.successMsg;
      if (successMsgEl && !successMsgEl.contains(event.target)) {
        this.editSuccess = false
      }
    }
  }
}
</script>

<style scoped>
.user-profile-editor {
  max-width: 500px;
  margin: 2rem auto;
  padding: 1.5rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  font-family: Arial, sans-serif;
}

.user-info-table {
  width: 100%;
  border-collapse: collapse;
}

.field-label {
  font-weight: bold;
  padding: 0.5rem;
  text-align: right;
  width: 30%;
  color: #333;
}

.field-value {
  padding: 0.5rem;
  cursor: pointer;
}

.field-value input {
  width: 100%;
  padding: 4px;
  font-size: 1em;
}

.update-button {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.update-button:hover {
  background: #45a049;
}

.error-message {
  color: red;
  margin-top: 1rem;
  font-weight: bold;
}

.success-message {
  color: greenyellow;
  margin-top: 1rem;
  font-weight: bold;
}
</style>