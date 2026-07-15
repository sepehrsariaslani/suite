<template>
	<Dialog
		v-model="showDialog"
		:title="__('Remove Participant')"
		size="sm"
	>
		<template #default>
			<div class="space-y-4">
				<p class="text-base text-ink-gray-7">
					{{ __('Remove {0} from the meeting?', [participantName]) }}
				</p>
				<FormControl
					:label="__('Ban from this meeting?')"
					type="checkbox"
					v-model="banFromMeeting"
				/>
			</div>
		</template>
		<template #actions>
			<div class="flex justify-end gap-2 w-full">
				<Button variant="subtle" @click="showDialog = false">{{ __('Cancel') }}</Button>
				<Button variant="solid" theme="red" @click="handleKickConfirm">{{ __('Remove') }}</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup lang="ts">
import { Button, Dialog, FormControl } from "frappe-ui";
import { computed, ref } from "vue";

interface Props {
	participantName: string;
	modelValue?: boolean;
}

interface Emits {
	(e: "update:modelValue", value: boolean): void;
	(e: "confirm", ban: boolean): void;
}

const props = withDefaults(defineProps<Props>(), {
	modelValue: false,
});

const emit = defineEmits<Emits>();

const banFromMeeting = ref(false);

const showDialog = computed({
	get: () => props.modelValue,
	set: (value: boolean) => emit("update:modelValue", value),
});

const handleKickConfirm = () => {
	emit("confirm", banFromMeeting.value);
	banFromMeeting.value = false;
	showDialog.value = false;
};
</script>
