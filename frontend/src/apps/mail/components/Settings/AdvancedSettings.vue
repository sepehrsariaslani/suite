<template>
	<h1>{{ __('API Access') }}</h1>
	<CopyControl v-if="user.data?.api_key" :label="__('API Key')" :value="user.data?.api_key" />
	<p v-else class="text-base">
		{{ __(`You don't have an API key yet. Generate one to access the API.`) }}
	</p>
	<Button
		class="min-h-7"
		:label="user.data?.api_key ? __('Regenerate Secret') : __('Generate Keys')"
		@click="generateKeys.submit()"
	/>

	<Dialog v-model="showSecret" :options="{ title: __('API Access') }">
		<template #body-content>
			<p class="text-base">
				{{ __(`Please copy the API secret now. You won’t be able to see it again!`) }}
			</p>
			<CopyControl :label="__('API Key')" :value="user.data?.api_key" />
			<CopyControl :label="__('API Secret')" :value="apiSecret" />
		</template>
	</Dialog>

	<template v-if="configRows.length">
		<h1>{{ __('Mail Client Configuration') }}</h1>
		<p class="text-ink-gray-6 text-base">
			{{
				__(
					'Use these details to connect a third-party mail client such as Thunderbird or the Gmail app.',
				)
			}}
		</p>
		<ListView
			class="max-w-full flex-1"
			:columns="CONFIG_COLUMNS"
			:rows="configRows"
			:options="{ selectable: false }"
			row-key="key"
		>
			<ListHeader />
			<ListRows>
				<ListRow v-for="row in configRows" :key="row.key" :row="row">
					<template #default="{ item }">
						<ListRowItem>
							<Tooltip :text="__('Click to copy')">
								<div
									class="cursor-copy truncate"
									@click="copyToClipBoard(String(item))"
								>
									{{ item }}
								</div>
							</Tooltip>
						</ListRowItem>
					</template>
				</ListRow>
			</ListRows>
		</ListView>
		<CopyControl :label="__('Username')" :value="user.data?.email" />
		<p class="text-ink-gray-5 text-sm">
			{{ __('Sign in using your existing mail account password.') }}
		</p>
	</template>
</template>
<script setup lang="ts">
import { computed, inject, ref } from 'vue'
import {
	Button,
	Dialog,
	ListHeader,
	ListRow,
	ListRowItem,
	ListRows,
	ListView,
	Tooltip,
	createResource,
} from 'frappe-ui'

import CopyControl from '@/apps/mail/components/Controls/CopyControl.vue'
import { copyToClipBoard } from '@/apps/mail/utils'

const user = inject('$user')

const showSecret = ref(false)
const apiSecret = ref('')

const generateKeys = createResource({
	url: 'suite.mail.utils.user.generate_user_keys',
	makeParams: () => ({ user: user.data?.name }),
	onSuccess: (data) => {
		if (!user.data?.api_key) user.reload()
		apiSecret.value = data.api_secret
		showSecret.value = true
	},
})

const CONFIG_COLUMNS = [
	{ label: __('Protocol'), key: 'protocol', width: '20%' },
	{ label: __('Hostname'), key: 'hostname', width: '40%' },
	{ label: __('Port'), key: 'port', width: '15%' },
	{ label: __('Security'), key: 'connection_security', width: '25%' },
]

const clientConfig = createResource({
	url: 'suite.mail.api.account.get_mail_client_config',
	auto: true,
})

const configRows = computed(() =>
	(clientConfig.data ?? []).map(
		(row: Record<string, string | number>, index: number) => ({
			...row,
			key: `${row.protocol}-${row.port}-${index}`,
		}),
	),
)
</script>
