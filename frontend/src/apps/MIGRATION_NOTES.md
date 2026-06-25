# frappe-ui v0 → v1 Migration Notes

## Scope
Migrating Drive and Writer apps. Token migration already done.

## Decisions

### 1. ui/drive Deduplication
**Decision**: Keep canonical files in `drive/ui/drive/`. Delete `writer/ui/drive/`. Writer imports repointed to `@/apps/drive/ui/drive/...`.

**Divergences merged into Drive's canonical version:**
- `RenameDialog.vue` + `MoveDialog.vue`: Keep Drive's local `@/apps/drive/utils/focus` (it has custom `getFirstFocusableElement` logic that the frappe-ui version may not have). Writer had switched to `focusDirective` from frappe-ui — we keep Drive's local implementation since it's more capable.
- `utils.js`: Updated to use `slugify` package (already in deps) — matches Writer's cleaner implementation.
- `Select/Select.vue`: Added `LucideCheck` import that Writer version had (used in the template for selected-item checkmark).
- `MoveDialog.vue`: Kept `'drive-Home'` route name (Drive-specific), not Writer's `'Home'`.

### 2. Dialog v0 → v1 Migration Rules Applied

| Old | New |
|---|---|
| `v-model="open"` | `v-model:open="open"` |
| `:options="{ title, size, actions }"` | `:title :size :actions` as flat props |
| `:options="dialogOptions"` (dynamic computed) | `v-bind="dialogOptions"` (spread) |
| `<template #body-content>` | Remove template, contents become default slot |
| `<template #body-title>` | `<template #title>` |

**Left unchanged** (not in migration docs): `#body-main`, `#body` slots in SearchPopup/SettingsDialog/MoveDialog/ShareDialog — these are custom overrides that bypass the body entirely.

**FDialogs pattern** (Drive + Writer both): `v-bind="dialog.options"` spread. The `component` key in options is handled separately as a slot condition.

### 3. Popover `#target` → `#trigger`
Applied to: `EmojiPicker.vue`, `SpacingDialog.vue`, `ColorPicker.vue`.

### 4. Icon String Migration
**Decision**: Convert all `:icon="LucideX"` Button props to `icon="lucide-x"` strings **where no extra props (class, etc.) are needed**. Skip `h(LucideX, { class: '...' })` usages — those need the wrapper for sizing.

Also fixed missing `lucide-` prefix on string icons (`icon="arrow-left"` → `icon="lucide-arrow-left"`).

In Dropdown/menu `icon:` fields — converted component refs to `"lucide-name"` strings throughout `Navbar.vue`, `ToC.vue`, `menu-buttons.js`, etc.

### 5. Editor Migration (TextEditor → Editor)

**New import path**: `frappe-ui/editor` (not `frappe-ui`)

**API changes applied:**
- `<TextEditor>` → `<Editor>`
- `<TextEditorFixedMenu :buttons="...">` → `<EditorFixedMenu :items="...">`
- `<TextEditorBubbleMenu>` → `<EditorBubbleMenu :items :options>`
- `:content` + `@change` → `v-model`
- Slot `#editor="{ editor }"` → default slot `#default="{ editor }"`
- `:bubble-menu` prop removed — use `<EditorBubbleMenu>` in default slot
- `:starterkit-options` removed — configure via `RichTextKit.configure(...)` in extensions array
- `:mentions` prop removed — configure via extension

**Menu buttons**: The old string-based format (`'Bold'`, `'Heading 1'`, etc.) is replaced with MenuItem objects imported from `frappe-ui/editor`. Predefined items: `Bold`, `Italic`, `Strike`, `InsertLink`, `Separator`, `BulletList`, `OrderedList`, `Blockquote`, `H1-H6`, `HeadingGroup`, `FontColor`, `InsertTable`, `InsertImage`, `HorizontalRule`, `Undo`, `Redo`.

**CoreEditor specifics:**
- `textEditor.value?.editor` → `textEditor.value?.editor` (same, Editor still exposes `editor`)
- `:bubble-menu` + `:bubble-menu-options` → `<EditorBubbleMenu :items :options>` inside default slot
- Custom menu items (PaintRoller, Settings, etc.) kept as `CommandMenuItem` objects with `action` callbacks
- `starterkit-options.trailingNode` + `starterkit-options.paragraph` moved to `RichTextKit.configure()` call in extensions array
- `:mentions` prop for user mentions — moved to extension config (using `MentionExtension.configure()` from the existing COMMON_EXTENSIONS)

**MarkdownEditor**: Simplified to use `articleToolbar` preset for `EditorFixedMenu`.

**CommentEditor**: Uses `commentToolbar` preset.

**VersionsSidebar**: Read-only editor, no menu needed. Just `<Editor v-model :extensions :editable="false">`.
