<template>
  <!-- '/suite' launcher: brand-logo app switcher for all 7 suite apps. -->
  <div class="h-full overflow-auto">
    <div class="mx-auto flex min-h-full max-w-5xl flex-col px-6 pt-[10%] pb-16">

      <div class="mx-auto grid grid-cols-4 gap-x-20 gap-y-10">
        <div class=" col-span-4">
          <TextInput placeholder="Search" variant="subtle">
            <template #prefix><span class="lucide-search size-4 text-ink-gray-4" /></template>
            </TextInput>

        </div>
        <router-link
          v-for="app in apps"
          :key="app.id"
          :to="app.prefix"
          class="group flex flex-col items-center text-center focus:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-3"
        >
          <div class="flex size-[3.375rem] items-center justify-center">
            <img
              :src="app.logo"
              :alt="`${app.name} logo`"
              class="size-[3.375rem] object-contain"
              draggable="false"
            />
          </div>
          <div class="mt-3 text-sm-medium leading-none text-ink-gray-9">{{ app.name }}</div>
        </router-link>

        <a
          href="/app/user-settings"
          class="group flex flex-col items-center text-center focus:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-3"
        >
          <div class="flex size-[3.375rem] items-center justify-center">
            <img
              :src="suiteLogo"
              alt="Settings logo"
              class="size-[3.375rem] object-contain"
              draggable="false"
            />
          </div>
          <div class="mt-3 text-sm-medium leading-none text-ink-gray-9">Settings</div>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { SUITE_APPS, SUITE_LOGO } from '@/apps/registry'
import { useRootStore } from '@/stores/root'
import { TextInput } from 'frappe-ui'

const apps = SUITE_APPS
const suiteLogo = SUITE_LOGO

onMounted(() => {
  useRootStore().setActiveApp(null)
})
</script>
