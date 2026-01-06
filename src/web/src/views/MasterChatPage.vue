<template>
  <div class="master-chat-page-wrapper mx-auto max-w-[1600px] px-3 pb-6 md:px-4 md:pb-8 lg:px-6 lg:pb-10">
    <section class="master-chat-page">
      <keep-alive>
        <MasterChat />
      </keep-alive>
    </section>
  </div>
</template>

<script setup lang="ts">
import MasterChat from '../components/MasterChat.vue';
</script>
