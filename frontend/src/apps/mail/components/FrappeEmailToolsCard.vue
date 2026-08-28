<template>
	<DashboardCard :title="__('Frappe Email')">
		<div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5">
			<a
				v-for="tool in FRAPPE_EMAIL_TOOLS"
				:key="tool.key"
				:href="tool.route"
				class="hover:bg-surface-gray-1 group flex items-center gap-3 border-b px-5 py-4 transition-colors sm:border-e xl:border-b-0 xl:last:border-e-0"
			>
				<div
					class="bg-surface-gray-2 text-ink-gray-6 flex h-9 w-9 shrink-0 items-center justify-center rounded-4"
				>
					<FeatherIcon :name="tool.icon" class="h-4 w-4" />
				</div>
				<span class="min-w-0 flex-1 text-sm font-medium">{{ tool.label }}</span>
				<FeatherIcon name="external-link" class="text-ink-gray-4 h-4 w-4 shrink-0" />
			</a>
		</div>
	</DashboardCard>
</template>

<script setup lang="ts">
import { Icon as FeatherIcon } from 'frappe-ui/experimental'

import { FRAPPE_EMAIL_TOOLS } from '@/apps/mail/frappeEmailTools'
import DashboardCard from '@/apps/mail/components/DashboardCard.vue'
</script>
