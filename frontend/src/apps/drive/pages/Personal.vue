<template>
  <GenericPage :get-entities="shareView ? getShared : getPersonal" :empty="shareView
    ? {
      icon: LucideUsers,
      title: 'No shared files',
      description: 'You can share files easily on Drive - try it out!',
    }
    : {
      icon: LucideHome,
      title: __('No files yet'),
      description: __('Upload to get started!'),
    }
    " :verify="!shareView && {
          data: {
            write: 1,
            upload: 1,
          },
        }
        " />
</template>

<script setup>
import { translate as __ } from '@/boot/translation'
import GenericPage from '@/apps/drive/components/GenericPage.vue'
import { getPersonal, getShared } from '@/apps/drive/resources/files'
import { shareView } from '@/apps/drive/data/prefs'
import { setCurrentFolder } from '@/apps/drive/data/currentFolder'
import LucideHome from '~icons/lucide/home'
import LucideUsers from '~icons/lucide/users'

setCurrentFolder({ name: '' })
</script>
