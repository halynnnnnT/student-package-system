<template>
    <div class="container">
      <h2>學生簽收包裹</h2>
  
      <!-- Search Filters -->
      <div class="search-section">
        <p>輸入您的學號或姓名查詢待簽收包裹：</p>
        <div class="search-inputs">

          <label for="search-student-name">姓名:</label>
          <input
            type="text"
            v-model="searchStudentNameInput"
            id="search-student-name"
            placeholder="輸入姓名"
          />

          <label for="search-student-id">學號:</label>
          <input
            type="text"
            v-model="searchStudentIdInput"
            id="search-student-id"
            placeholder="輸入學號"
          />
  
          
          <button @click="clearSearch" class="clear-search-btn">清除查詢</button>
        </div>
      </div>
  
      <div v-if="loading" class="loading">載入中...</div>
      <div v-else-if="filteredPackages.length === 0 && (searchStudentIdInput || searchStudentNameInput) && !error" class="no-data">
        根據您的查詢，找不到待簽收的包裹。
      </div>
      <div v-else-if="filteredPackages.length === 0 && !error" class="no-data">
        目前沒有待簽收的包裹。
      </div>
      <div v-else-if="error" class="error-message">{{ error }}</div>
      <table v-else class="pickup-table">
        <thead>
          <tr>
            <th>數量</th> <!-- NEW Column Header -->
            <th>寢室</th>
            <th>學生姓名</th>
            <th>學號</th>
            <th>包裹描述</th>
            <th>送達日期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pkg in filteredPackages" :key="pkg.id">
            <td>{{ pkg.quantity }}</td> <!-- NEW Data Cell -->
            <td>{{ pkg.room_num || "N/A" }}</td>
            <td>{{ pkg.student_name }}</td>
            <td>{{ pkg.student_id }}</td>
            <td>{{ pkg.package_description }}</td>
            <td>{{ formatDate(pkg.arrival_date) }}</td>
            <td>
              <button
                @click="pickupPackage(pkg.id)"
                :disabled="pkg.signing"
                class="pickup-button"
              >
                {{ pkg.signing ? "處理中..." : "簽收" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p
        v-if="pickupMessage"
        :class="{
          'success-message': isPickupSuccess,
          'error-message': !isPickupSuccess,
        }"
      >
        {{ pickupMessage }}
      </p>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from "vue"; // Added computed
  import axios from "axios";
  
  const allPendingPackages = ref([]); // Store all fetched packages
  const loading = ref(true);
  const error = ref("");
  const pickupMessage = ref("");
  const isPickupSuccess = ref(false);
  
  // Refs for search inputs
  const searchStudentIdInput = ref("");
  const searchStudentNameInput = ref("");
  
  const fetchAllPendingPackages = async () => { // Renamed for clarity
    loading.value = true;
    error.value = "";
    allPendingPackages.value = []; // Clear previous results
    try {
      // You are using the general pending endpoint
      const response = await axios.get("/api/packages/pending");
      allPendingPackages.value = response.data.map((pkg) => ({
        ...pkg,
        signing: false,
      }));
    } catch (err) {
      console.error("Error fetching packages for pickup:", err);
      // Removed 401 specific message as this page doesn't assume login yet
      error.value = "無法載入待簽收包裹列表。";
    } finally {
      loading.value = false;
    }
  };
  
  // Computed property to filter packages based on search inputs
  const filteredPackages = computed(() => {
    if (!allPendingPackages.value) return [];
  
    let packages = [...allPendingPackages.value];
  
    const searchId = searchStudentIdInput.value.trim().toLowerCase();
    const searchName = searchStudentNameInput.value.trim().toLowerCase();
  
    if (searchId) {
      packages = packages.filter(
        (pkg) => pkg.student_id && pkg.student_id.toLowerCase().includes(searchId)
      );
    }
  
    if (searchName) {
      packages = packages.filter(
        (pkg) => pkg.student_name && pkg.student_name.toLowerCase().includes(searchName)
      );
    }
    // If both search fields are empty, show all packages
    return packages;
  });
  
  const clearSearch = () => {
    searchStudentIdInput.value = "";
    searchStudentNameInput.value = "";
    // The computed property filteredPackages will automatically update
  };
  
  
  const pickupPackage = async (packageId) => {
    // Find in the original list or filtered list, doesn't matter much here
    const pkg = allPendingPackages.value.find((p) => p.id === packageId);
    if (pkg) {
      pkg.signing = true;
    }
    pickupMessage.value = "";
  
    try {
      const response = await axios.post(`/api/packages/pickup/${packageId}`);
      pickupMessage.value = response.data.message || "包裹已成功簽收！";
      isPickupSuccess.value = true;
      await fetchAllPendingPackages(); // Refresh the list
    } catch (err) {
      pickupMessage.value = err.response?.data?.error || "簽收失敗。";
      isPickupSuccess.value = false;
      console.error("Error picking up package:", err);
      if (pkg) {
        pkg.signing = false;
      }
    }
  };
  
  const formatDate = (dateString) => {
    if (!dateString) return "";
    const options = {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    };
    return new Date(dateString).toLocaleString("zh-TW", options);
  };
  
  onMounted(() => {
    fetchAllPendingPackages(); // Fetch all packages on mount
  });
  </script>
  
  <style scoped>
  .container {
    max-width: 900px;
    margin: 20px auto;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .container h2 {
    margin-top: 0;
    color: #333;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
    margin-bottom: 20px;
  }
  
  /* Search Section Styles */
  .search-section {
    margin-bottom: 25px;
    padding: 15px;
    background-color: #f0f8ff; /* Light alice blue background */
    border-radius: 5px;
    border: 1px solid #d1e0ff;
  }
  .search-section p {
      margin-top: 0;
      margin-bottom: 10px;
      font-weight: bold;
      color: #333;
  }
  
  .search-inputs {
    display: flex;
    gap: 15px; /* Spacing between items */
    align-items: center; /* Align items vertically */
    flex-wrap: wrap; /* Allow wrapping on smaller screens */
  }
  
  .search-inputs label {
    margin-right: 5px;
    font-weight: 500;
  }
  
  .search-inputs input[type="text"] {
    padding: 8px 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    min-width: 180px; /* Give inputs a decent base width */
  }
  
  .clear-search-btn {
    padding: 8px 15px;
    background-color: #6c757d; /* Bootstrap secondary color */
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s ease-in-out;
  }
  .clear-search-btn:hover {
    background-color: #5a6268;
  }
  
  
  .pickup-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    margin-bottom: 20px;
  }
  
  .pickup-table th,
  .pickup-table td {
    border: 1px solid #ddd;
    padding: 10px 12px;
    text-align: left;
    vertical-align: middle;
  }
  
  .pickup-table th {
    background-color: #f0f0f0;
    font-weight: bold;
    color: #333;
  }
  
  .pickup-table tr:nth-child(even) {
    background-color: #f8f8f8;
  }
  
  .pickup-table tr:hover {
    background-color: #f1f1f1;
  }
  
  .pickup-button {
    padding: 6px 12px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s ease-in-out;
    font-size: 0.9em;
  }
  
  .pickup-button:hover:not(:disabled) {
    background-color: #218838;
  }
  
  .pickup-button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .success-message {
    color: green;
    margin-top: 10px;
    padding: 10px;
    background-color: #e6ffed;
    border: 1px solid #5cb85c;
    border-radius: 4px;
  }
  
  .error-message {
    color: red;
    margin-top: 10px;
    padding: 10px;
    background-color: #fdeded;
    border: 1px solid #d9534f;
    border-radius: 4px;
  }
  
  .loading,
  .no-data {
    text-align: center;
    padding: 20px;
    color: #666;
    font-style: italic;
    background-color: #fff;
    border: 1px solid #eee;
    border-radius: 4px;
  }
  </style>