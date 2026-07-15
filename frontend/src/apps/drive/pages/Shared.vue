<template>
  <GenericPage :get-entities :empty />
</template>

<script setup>
import GenericPage from '@/apps/drive/components/GenericPage.vue'
import { computed } from 'vue'
import { getSiteFiles, getShared } from '@/apps/drive/resources/files'
import { shareView } from '@/apps/drive/data/prefs'
import LucideFiles from '~icons/lucide/files'


const getEntities = computed(() =>
  shareView.value ? getShared : getSiteFiles
)
const empty = computed(() =>
  shareView.value
    ? {
      icon: LucideUsers,
      title: __('No shared files'),
      description: __('You can share files easily on Drive - try it out!'),
    }
    : {
      icon: LucideFiles,
      title: __('No files on site yet'),
      description: __('Upload to get started!'),
    }
)
</script>
