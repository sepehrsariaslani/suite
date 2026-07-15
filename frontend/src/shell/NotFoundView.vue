<template>
  <div class="flex h-full flex-col items-center justify-center gap-3 p-8">
    <h1 class="text-3xl-semibold text-ink-gray-9">{{ __('Page not found') }}</h1>
    <router-link to="/suite" class="text-sm text-ink-blue-link hover:underline">
      {{ __('Back to launcher') }}
    </router-link>
  </div>
</template>
