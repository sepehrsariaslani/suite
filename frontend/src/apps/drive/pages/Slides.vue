<template>
  <GenericPage
    :get-entities="getSlides"
    :empty="{
      icon: LucideGalleryVerticalEnd,
      title: __('No presentations yet'),
      description: __('Create presentations using Slides.')
    }"
  />
</template>
<script setup>
import GenericPage from '@/apps/drive/components/GenericPage.vue'
import LucideGalleryVerticalEnd from '~icons/lucide/gallery-vertical-end'
import { getSlides } from '@/apps/drive/resources/files'
</script>
