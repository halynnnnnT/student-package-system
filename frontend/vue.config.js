const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': { // 所有 /api 開頭的請求都會被代理
        target: 'http://localhost:5000', // Flask 後端地址
        changeOrigin: true,
        // pathRewrite: { '^/api': '' } // 如果後端 API 沒有 /api 前綴，則需要重寫路徑
      }
    }
  }
})