<template>
  <div id="app">
    <nav>
      <router-link to="/admin">管理者頁面</router-link> |
      <router-link to="/pickup">學生簽收頁面</router-link>
    </nav>
    <router-view/>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
