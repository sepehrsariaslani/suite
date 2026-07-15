<template>
	<component
		:is="isMobile ? SearchMobileLayout : Dialog"
		v-model="show"
		:options="{ size: '2xl', paddingTop: '2%' }"
	>
		<template #body>
			<div class="bg-surface-base">
				<div
					class="flex items-center px-4 py-2"
					:class="{
						'border-b': showAdvancedFilters || results?.data?.length || activeFilters.length,
					}"
				>
					<Button v-if="isMobile" variant="ghost" @click="show = false">
						<template #icon>
							<ChevronLeft class="text-ink-gray-5 h-4 w-4" />
						</template>
					</Button>
					<Search v-else class="text-ink-gray-5 h-4 w-4" />
					<input
						ref="searchInput"
						v-model="filter.text"
						icon-left="search"
						type="search"
						class="placeholder-ink-gray-4 w-full border-none bg-transparent text-base focus:ring-0"
						placeholder="Search"
						@click="showAdvancedFilters = false"
						@keyup.enter="openSearchPage"
					/>
					<Button variant="ghost" @click="showAdvancedFilters = !showAdvancedFilters">
						<template #icon>
							<SlidersHorizontal class="text-ink-gray-5 h-4 w-4" />
						</template>
					</Button>
				</div>
				<div
					v-if="!showAdvancedFilters && activeFilters.length"
					class="flex flex-wrap gap-1.5 px-4 py-2"
				>
					<span
						v-for="chip in activeFilters"
						:key="chip.key"
						class="bg-surface-gray-2 text-ink-gray-7 inline-flex items-center gap-1 rounded py-0.5 pl-2 pr-1 text-xs"
					>
						<span class="max-w-40 truncate">{{ chip.label }}</span>
						<button
							class="rounded p-0.5"
							:aria-label="__('Remove filter')"
							@click="removeFilter(chip.key)"
						>
							<X class="size-3" />
						</button>
					</span>
				</div>
				<template v-if="showAdvancedFilters">
					<div class="space-y-4 p-4">
						<Switch
							v-if="hasMultipleAccounts"
							v-model="allAccounts"
							:label="__('Search across all accounts')"
							:description="
								__('Look through every account you own — slower, but finds a mail wherever it landed.')
							"
							class="!p-0"
						/>
						<FormControl
							v-if="!allAccounts"
							v-model="filter.inMailbox"
							type="select"
							:label="__('Look In')"
							:options="mailboxOptions"
						/>
						<FormControl v-model="filter.subject" :label="__('Subject')" />
						<FormControl v-model="filter.from" :label="__('From')" />
						<FormControl v-model="filter.to" :label="__('To')" />
						<div class="flex space-x-4">
							<FormControl v-model="filter.cc" :label="__('Cc')" class="w-full" />
							<FormControl v-model="filter.bcc" :label="__('Bcc')" class="w-full" />
						</div>
						<div class="flex space-x-4">
							<FormControl
								v-model="filter.after"
								type="date"
								:label="__('From Date')"
								class="w-full"
							/>
							<FormControl
								v-model="filter.before"
								type="date"
								:label="__('To Date')"
								class="w-full"
							/>
						</div>
						<FormControl
							v-model="filter.hasAttachment"
							type="select"
							:label="__('Attachments')"
							:options="getAttachmentOptions()"
						/>
						<FormControl
							v-model="filter.isRead"
							type="select"
							:label="__('Read Status')"
							:options="getReadStatusOptions()"
						/>
					</div>
					<div
						class="flex w-full p-4"
						:class="isMobile ? 'flex-col space-y-4' : 'justify-end space-x-4'"
					>
						<Button
							:label="__('Clear Filters')"
							class="w-full sm:w-28"
							@click="Object.assign(filter, getDefaultFilter(true))"
						/>
						<Button
							:label="__('Search')"
							variant="solid"
							class="w-full sm:w-28"
							@click="openSearchPage"
						/>
					</div>
				</template>
				<div
					v-else-if="results?.data?.[0]?.length"
					class="px-2 pb-2"
					:class="{ 'pt-2': !activeFilters.length }"
				>
					<div
						v-for="(result, idx) in results.data[0]"
						:key="idx"
						class="hover:bg-surface-gray-1 group flex rounded p-2 hover:cursor-pointer"
						@click="openThread(result)"
					>
						<div class="mr-2 space-y-1 truncate">
							<p class="truncate text-base-semibold">
								{{ result.subject || __('[No subject]') }}
							</p>
							<div class="flex items-center gap-1 truncate text-sm">
								<span class="truncate">{{ getInterlocutors(result) }}</span>
								<template v-if="allAccounts && result.account_name">
									<span aria-hidden="true" class="text-ink-gray-4">•</span>
									<span class="text-ink-gray-4 shrink-0 text-xs">
										{{ __('in {0}', [result.account_name]) }}
									</span>
								</template>
							</div>
							<div
								v-for="m in result.mailboxes"
								:key="m.mailbox_id"
								class="bg-surface-gray-2 group-hover:bg-surface-gray-3 mr-1.5 inline-flex rounded p-1 text-xs"
							>
								{{ m.mailbox_name }}
							</div>
						</div>
						<div
							class="text-ink-gray-4 ml-auto flex shrink-0 flex-col justify-between text-xs"
						>
							<span>{{ getFormattedDate(result.received_at) }}</span>
							<div
								v-if="noOfAttachments(result)"
								class="ml-auto flex items-center space-x-1"
							>
								<Paperclip class="text-ink-gray-4 h-3.5 w-3.5" />
								<span>{{ noOfAttachments(result) }}</span>
							</div>
						</div>
					</div>
					<div
						v-if="results.data[1] > 5"
						class="text-ink-gray-4 my-2 text-center text-sm"
					>
						{{ __('Showing top 5 results. ') }}
						<a class="cursor-pointer hover:underline" @click="openSearchPage">
							{{ __('View more.') }}
						</a>
					</div>
				</div>
				<div
					v-else-if="!results?.loading && results?.data?.[1] === 0"
					class="text-ink-gray-4 py-4 text-center text-sm"
				>
					{{ __('No results found for the given query.') }}
				</div>
			</div>
		</template>
	</component>
</template>

<script setup lang="ts">
import { computed, nextTick, reactive, ref, useTemplateRef, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { watchDebounced } from '@vueuse/core'
import { ChevronLeft, Paperclip, Search, SlidersHorizontal, X } from 'lucide-vue-next'
import { Button, Dialog, FormControl, Switch, createResource } from 'frappe-ui'

import { getAttachmentOptions, getReadStatusOptions } from '@/apps/mail/constants'
import { getFormattedDate } from '@/apps/mail/utils'
import { useScreenSize } from '@/apps/mail/utils/composables'
import { userStore } from '@/apps/mail/stores/user'
import SearchMobileLayout from '@/apps/mail/components/SearchMobileLayout.vue'

import type { Recipient } from '@/apps/mail/types'

const show = defineModel<boolean>()

// Read store.accountId live in makeParams; destructuring would snapshot the
// unwrapped value and miss account switches while this modal stays mounted.
const store = userStore()
const { mailboxes } = store

const route = useRoute()
const { isMobile } = useScreenSize()

const searchInput = useTemplateRef('searchInput')
watch(show, (val) => {
	if (val) nextTick(() => searchInput.value?.focus())
})

const getDefaultFilter = (reset = false) =>
	Object.fromEntries(
		[
			'text',
			'inMailbox',
			'subject',
			'from',
			'to',
			'cc',
			'bcc',
			'after',
			'before',
			'hasAttachment',
			'isRead',
		].map((key) => [key, reset ? '' : route.query[key] || '']),
	)

const filter = reactive({ ...getDefaultFilter() })
const filteredFilter = computed(() =>
	Object.fromEntries(
		Object.entries(filter)
			.map(([k, v]) => [k, typeof v === 'string' ? v.trim() : v])
			.filter(([, v]) => Boolean(v)),
	),
)

// Cross-account search: an opt-in that fans the query out across every account (defaulting off, so a
// search stays scoped to the current account for speed). Persisted, and pre-checked when the search
// page was opened with the flag set, so reopening the dialog reflects the active scope.
const ALL_ACCOUNTS_STORAGE_KEY = 'mail-search-all-accounts'
const hasMultipleAccounts = computed(() => (store.userResource.data?.accounts?.length ?? 0) > 1)
const allAccounts = ref(
	hasMultipleAccounts.value &&
		(route.query.all_accounts != null ||
			localStorage.getItem(ALL_ACCOUNTS_STORAGE_KEY) === 'true'),
)
watch(allAccounts, (val) => {
	localStorage.setItem(ALL_ACCOUNTS_STORAGE_KEY, String(val))
	// "Look In" targets a folder in the current account; it can't carry across accounts, so drop it.
	if (val) filter.inMailbox = ''
	if (filter.text) results.reload()
})

const showAdvancedFilters = ref(false)

const mailboxOptions = computed(() =>
	[{ label: __('All folders'), value: '' }].concat(
		mailboxes.data.map((m: { id: string; _name: string }) => ({
			label: m._name,
			value: m.id,
		})),
	),
)

// Active advanced filters as removable chips, shown under the search box (collapsed view) so a single
// filter can be cleared without opening the whole panel.
const FILTER_LABELS: Record<string, string> = {
	inMailbox: __('In'),
	subject: __('Subject'),
	from: __('From'),
	to: __('To'),
	cc: __('Cc'),
	bcc: __('Bcc'),
	after: __('After'),
	before: __('Before'),
}

const optionLabel = (options: { label: string; value: string }[], value: string) =>
	options.find((o) => o.value === value)?.label ?? value

const activeFilters = computed(() =>
	Object.entries(filteredFilter.value)
		.filter(([key]) => key !== 'text')
		.map(([key, value]) => {
			// hasAttachment/isRead values ("Without Attachments", "Unread") are self-descriptive, so show
			// them on their own — the rest get a "Field: value" label.
			if (key === 'hasAttachment') return { key, label: optionLabel(getAttachmentOptions(), value) }
			if (key === 'isRead') return { key, label: optionLabel(getReadStatusOptions(), value) }
			const display = key === 'inMailbox' ? optionLabel(mailboxOptions.value, value) : value
			return { key, label: `${FILTER_LABELS[key]}: ${display}` }
		}),
)

const removeFilter = (key: string) => {
	filter[key] = ''
	if (filter.text) results.reload()
}

const results = createResource({
	url: 'suite.mail.api.mail.search_mails',
	makeParams: () => ({
		account: store.accountId,
		filter: filteredFilter.value,
		all_accounts: allAccounts.value,
	}),
})

// The query the results page reads to reproduce this search: the trimmed filters plus, when on, the
// cross-account flag (kept out of `filter` so it never becomes a JMAP search condition on the server).
const searchQuery = computed(() => ({
	...filteredFilter.value,
	...(allAccounts.value ? { all_accounts: '1' } : {}),
}))

const noOfAttachments = (result) =>
	result.attachments?.filter((m) => m.filename && m.disposition === 'attachment').length || 0

watchDebounced(
	() => filter.text,
	(val) => {
		if (val) results.reload()
		else results.reset()
	},
	{ debounce: 250 },
)

const openSearchPage = () => {
	router.push({
		name: 'mail-mailbox',
		params: { accountId: store.accountId, mailbox: 'search' },
		query: searchQuery.value,
	})
	show.value = false
}

const router = useRouter()

// Open the result in its own account (tagged by the server) — for a cross-account search that may
// differ from the active account; the mailbox route's guard switches to it.
const openThread = (result: { account: string; thread_id: string }) => {
	router.push({
		name: 'mail-mail',
		params: { accountId: result.account, mailbox: 'search', threadID: result.thread_id },
		query: searchQuery.value,
	})
	show.value = false
}

const getInterlocutors = (result: {
	from_name?: string
	from_email: string
	recipients?: Recipient[]
}) => {
	const sender = result.from_name || result.from_email
	if (!result.recipients?.length) return sender

	const seen = new Set<string>()
	const recipients = result.recipients
		.filter((r) => r.email !== result.from_email && !seen.has(r.email) && seen.add(r.email))
		.map((r) => r.display_name || r.email)
		.join(', ')

	return `${sender}, ${recipients}`
}
</script>
