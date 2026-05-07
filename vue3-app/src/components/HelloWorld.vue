<script setup>
defineProps({
  msg: String
})
</script>

<template>
  <div class="hello">
    <p class="msg">{{ msg }}</p>
    <p>
      编辑 <code>src/App.vue</code> 开始你的 Vue 3 之旅
    </p>
  </div>
</template>

<style scoped>
.hello {
  margin-top: 2rem;
}
.msg {
  font-size: 1.5rem;
  color: #42b883;
  font-weight: bold;
}
code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
