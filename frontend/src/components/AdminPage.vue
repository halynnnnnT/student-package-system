<template>
    <div class="container">
      <h2>管理者頁面</h2>
  
      <!-- Student Search and List Section -->
      <div class="student-management-section">
        <h3>學生列表與查詢</h3>
        <div class="search-filters">

          <label for="search-room-num">查詢寢室:</label> <!-- 新增 -->
          <input
            type="text"
            v-model="searchRoomNumInput"
            id="search-room-num"
            placeholder="輸入寢室號"
            @input="filterStudents"
          />

          <label for="search-student-id">查詢學號:</label>
          <input
            type="text"
            v-model="searchStudentIdInput"
            id="search-student-id"
            placeholder="輸入學號"
            @input="filterStudents"
          />
  
          <label for="search-student-name">查詢姓名:</label>
          <input
            type="text"
            v-model="searchStudentNameInput"
            id="search-student-name"
            placeholder="輸入姓名"
            @input="filterStudents"
          />
  
          
  
          <button @click="clearSearch" class="clear-search-btn">
            清除查詢
          </button>
        </div>
  
        <div v-if="loadingStudents" class="loading">載入學生列表中...</div>
        <div
          v-else-if="displayedStudents.length === 0 && (searchStudentIdInput || searchStudentNameInput || searchRoomNumInput)"
          class="no-data"
        >
          查無此學生。
        </div>
        <div v-else-if="displayedStudents.length === 0" class="no-data">
          目前沒有學生資料。
        </div>
        <div v-else-if="studentListError" class="error-message">
          {{ studentListError }}
        </div>
        <table v-else class="students-table">
          <thead>
            <tr>
              <th>寢室</th>
              <th>姓名</th>
              <th>學號</th>
              
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="student in displayedStudents"
              :key="student.id"
              :class="{ 'selected-row': selectedStudentForPackageInfo?.id === student.id }"
            >
              <td>{{ student.room_num || 'N/A' }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.student_id }}</td>
              
              <td>
                <button @click="selectStudentForPackage(student)">
                  選擇此學生添加包裹
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- Add Package Section -->
    <div v-if="selectedStudentForPackageInfo" class="add-package-section">
      <h3>
        為 {{ selectedStudentForPackageInfo.name }} ({{
          selectedStudentForPackageInfo.student_id
        }}{{ selectedStudentForPackageInfo.room_num ? ' - ' + selectedStudentForPackageInfo.room_num : '' }}) 添加包裹
      </h3>
      <div>
        <label for="package-desc">包裹描述:</label>
        <input
          type="text"
          v-model="packageDescription"
          id="package-desc"
          placeholder="例如：來自 PChome 的書籍"
        />

        <label for="package-quantity">數量:</label> <!-- NEW Quantity Input -->
        <input
          type="number"
          v-model.number="packageQuantity"
          id="package-quantity"
          min="1"
          placeholder="1"
        />

        <button
          @click="addPackage"
          :disabled="!selectedStudentId || !packageDescription || packageQuantity < 1"
        >
          添加到待簽收
        </button>
      </div>
      <p
        v-if="addPackageMessage"
        :class="{
          'success-message': isAddPackageSuccess,
          'error-message': !isAddPackageSuccess,
        }"
      >
        {{ addPackageMessage }}
      </p>
    </div>
      <div v-else class="add-package-section placeholder">
          <p>請從上方列表選擇一位學生以添加包裹。</p>
      </div>
  
  
      <!-- Pending Packages List Section -->
      <div class="pending-packages-section">
        <h3>目前待簽收包裹</h3>
        <div v-if="loadingPending" class="loading">載入中...</div>
        <div
          v-else-if="pendingPackages.length === 0 && !pendingError"
          class="no-data"
        >
          目前沒有待簽收的包裹。
        </div>
        <div v-else-if="pendingError" class="error-message">
          {{ pendingError }}
        </div>
        <table v-else>
          <thead>
            <tr>
              <th>數量</th>
              <th>學生姓名</th>
              <th>學號</th>
              <th>寢室號</th>
              <th>包裹描述</th>
              <th>送達日期</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pkg in pendingPackages" :key="pkg.id">
              <td>{{ pkg.quantity }}</td>
              <td>{{ pkg.student_name }}</td>
              <td>{{ pkg.student_id }}</td>
              <td>{{ pkg.room_num || 'N/A' }}</td>
              <td>{{ pkg.package_description }}</td>
              <td>{{ formatDate(pkg.arrival_date) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from "vue";
  import axios from "axios";
  
  // Student list and search
  const allStudents = ref([]);
  const loadingStudents = ref(true);
  const studentListError = ref("");
  const searchStudentIdInput = ref("");
  const searchStudentNameInput = ref("");
  const searchRoomNumInput = ref(""); // 新增 ref for room number search
  
  // For adding a package
  const packageQuantity = ref(1); // NEW: ref for package quantity, default to 1
  const selectedStudentId = ref("");
  const selectedStudentForPackageInfo = ref(null);
  const packageDescription = ref("");
  const addPackageMessage = ref("");
  const isAddPackageSuccess = ref(false);
  
  // Pending packages
  const pendingPackages = ref([]);
  const loadingPending = ref(true);
  const pendingError = ref("");
  
  const fetchAllStudents = async () => {
    loadingStudents.value = true;
    studentListError.value = "";
    try {
      const response = await axios.get("/api/students");
      allStudents.value = response.data;
    } catch (error) {
      console.error("Error fetching students:", error);
      studentListError.value = "無法載入學生列表。";
    } finally {
      loadingStudents.value = false;
    }
  };
  
  // 將 displayedStudents 改為一個 ref，並創建一個函數來更新它
  // 這樣可以避免在模板的 @input 中直接調用 computed property (雖然技術上可行，但分離邏輯更清晰)
  const internalDisplayedStudents = ref([]);
  
  const filterStudents = () => {
    if (!allStudents.value) {
      internalDisplayedStudents.value = [];
      return;
    }
    let filtered = [...allStudents.value]; // Create a shallow copy to avoid modifying original
  
    const searchId = searchStudentIdInput.value.trim().toLowerCase();
    const searchName = searchStudentNameInput.value.trim().toLowerCase();
    const searchRoom = searchRoomNumInput.value.trim().toLowerCase(); // 新增
  
    if (searchId) {
      filtered = filtered.filter((student) =>
        student.student_id.toLowerCase().includes(searchId)
      );
    }
    if (searchName) {
      filtered = filtered.filter((student) =>
        student.name.toLowerCase().includes(searchName)
      );
    }
    if (searchRoom) { // 新增寢室號過濾邏輯
      filtered = filtered.filter((student) =>
        student.room_num && student.room_num.toLowerCase().includes(searchRoom)
      );
    }
    internalDisplayedStudents.value = filtered;
  };
  
  // 使用 computed property 來暴露 internalDisplayedStudents，使其在模板中響應式
  const displayedStudents = computed(() => internalDisplayedStudents.value);
  
  
  const clearSearch = () => {
    searchStudentIdInput.value = "";
    searchStudentNameInput.value = "";
    searchRoomNumInput.value = ""; // 新增
    filterStudents(); // 清除後重新過濾，顯示所有學生
  };
  
  const selectStudentForPackage = (student) => {
    selectedStudentId.value = student.id;
    selectedStudentForPackageInfo.value = student;
    packageDescription.value = "";
    addPackageMessage.value = "";
    selectedStudentForPackageInfo.value = student; packageQuantity.value = 1; /* Reset quantity */
  };
  
  const fetchPendingPackages = async () => {
    loadingPending.value = true;
    pendingError.value = "";
    try {
      const response = await axios.get("/api/packages/pending");
      pendingPackages.value = response.data;
    } catch (error) {
      console.error("Error fetching pending packages:", error);
      pendingError.value = "無法載入待簽收包裹列表。";
    } finally {
      loadingPending.value = false;
    }
  };
  
  const addPackage = async () => {
  if (!selectedStudentId.value || !packageDescription.value || !packageQuantity.value || packageQuantity.value < 1) {
    addPackageMessage.value = "請選擇學生、填寫包裹描述並確保數量至少為 1。";
    isAddPackageSuccess.value = false;
    return;
  }
  try {
    const response = await axios.post("/api/packages/add", {
      student_db_id: selectedStudentId.value,
      package_description: packageDescription.value,
      quantity: packageQuantity.value, // SEND quantity to backend
    });
    addPackageMessage.value = response.data.message || "包裹已成功添加！";
    isAddPackageSuccess.value = true;

    packageDescription.value = "";
    packageQuantity.value = 1; // Reset quantity input
    // Optionally keep student selected or clear:
    // selectedStudentId.value = '';
    // selectedStudentForPackageInfo.value = null;

    fetchPendingPackages();
  } catch (error) {
    addPackageMessage.value =
      error.response?.data?.error || "添加包裹失敗。";
    isAddPackageSuccess.value = false;
    console.error("Error adding package:", error);
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
  
  onMounted(async () => {
    await fetchAllStudents(); // 等待學生數據加載完成
    filterStudents(); // 初始加載後執行一次過濾 (顯示所有學生)
    fetchPendingPackages();
  });
  </script>
  
  <style scoped>
  .container > div {
    margin-bottom: 30px;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .container h2,
  .container h3 {
    margin-top: 0;
    color: #333;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
    margin-bottom: 15px;
  }
  
  .search-filters {
    display: flex;
    gap: 15px;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }
  
  .search-filters label {
    margin-right: 5px;
    font-weight: bold;
  }
  
  .search-filters input[type="text"] {
    padding: 8px 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    min-width: 150px; /* 調整為 min-width 以適應不同長度的 placeholder */
  }
  
  /* 確保每個查詢條件佔據合理空間 */
  .search-filters > div, .search-filters > label + input {
      margin-bottom: 10px; /* 如果換行，給予垂直間距 */
  }
  
  
  .search-filters button,
  .students-table button,
  .add-package-section button {
    padding: 8px 15px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s ease-in-out;
  }

  .search-filters button:hover,
  .students-table button:hover,
  .add-package-section button:hover {
    background-color: #0056b3;
  }
  
  .search-filters button:disabled,
  .add-package-section button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .clear-search-btn {
    background-color: #6c757d;
  }
  .clear-search-btn:hover {
    background-color: #545b62;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
  }
  
  th,
  td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
  }
  
  th {
    background-color: #f0f0f0;
    font-weight: bold;
  }
  
  tr:nth-child(even) {
    background-color: #f8f8f8;
  }
  tr.selected-row {
    background-color: #d1ecf1 !important;
    font-weight: bold;
  }
  
  .add-package-section div > label {
    margin-right: 5px;
    display: inline-block;
    margin-bottom: 5px;
  }
  .add-package-section div > input[type="text"] {
    padding: 8px 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-right: 10px;
    min-width: 250px;
  }
  
  .add-package-section.placeholder p {
      color: #666;
      font-style: italic;
  }
  
  
  .success-message {
    color: green;
    margin-top: 10px;
    font-weight: bold;
  }
  
  .error-message {
    color: red;
    margin-top: 10px;
    font-weight: bold;
  }
  
  .loading,
  .no-data {
    text-align: center;
    padding: 20px;
    color: #666;
    font-style: italic;
  }

  .add-package-section label { /* Make labels behave a bit better */
    display: block;
    margin-top: 10px;
    margin-bottom: 3px;
  }
  .add-package-section input[type="text"],
  .add-package-section input[type="number"] {
    width: calc(100% - 22px); /* Adjust for padding/border */
    padding: 8px 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-bottom: 10px;
  }
  .add-package-section input[type="number"] {
    max-width: 100px; /* Quantity input doesn't need to be super wide */
  }
  </style>