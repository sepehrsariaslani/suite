<template>
	<div class="flex min-h-full items-center justify-center p-6">
		<div
			class="w-full max-w-xl rounded-2xl border border-outline-gray-2 bg-surface-base p-8 text-center shadow-sm"
		>
			<div
				class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-gray-2"
			>
				<LucideCalendar class="h-8 w-8 text-ink-gray-7" />
			</div>
			<h1 class="mb-3 text-2xl font-semibold text-ink-gray-9">
				{{ __('Calendar is not set up yet') }}
			</h1>
			<p class="mx-auto mb-6 max-w-lg text-sm leading-6 text-ink-gray-6">
				{{
					__(
						'No mail/calendar account is assigned to your user on this site yet. Set up a mail account first, then Calendar will become available here.',
					)
				}}
			</p>
			<div class="flex justify-center gap-3">
				<Button variant="solid" @click="router.push('/mail')">
					{{ __('Open Mail') }}
				</Button>
				<Button variant="subtle" @click="router.push('/suite')">
					{{ __('Back to Suite') }}
				</Button>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { Button } from 'frappe-ui'
import { useRouter } from 'vue-router'
import LucideCalendar from '~icons/lucide/calendar'

const router = useRouter()
</script>
