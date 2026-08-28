from pathlib import Path
from unittest import TestCase

from scripts.audit_persian_mail import candidates_from_source


class TestDirectUICandidateAudit(TestCase):
    def candidate_texts(self, source: str, name: str = "Member.vue") -> list[str]:
        return [candidate.text for candidate in candidates_from_source(Path(name), source)]

    def test_reports_direct_vue_text_and_literal_attributes(self):
        source = """
<template>
  <Button label="Add Member" title="Invite a teammate">Welcome</Button>
  <input placeholder="Search messages" aria-label="Close dialog" />
</template>
"""

        self.assertEqual(
            self.candidate_texts(source),
            ["Add Member", "Invite a teammate", "Welcome", "Search messages", "Close dialog"],
        )

    def test_reports_user_facing_script_properties(self):
        source = """
const action = {
  label: 'Retry delivery',
  description: "Try sending this message again",
  message: `The request failed`,
}
"""

        self.assertEqual(
            self.candidate_texts(source, "Actions.ts"),
            ["Retry delivery", "Try sending this message again", "The request failed"],
        )

    def test_ignores_translated_bindings_and_technical_content(self):
        source = """
<template>
  <Button :label="__('Add Member')" />
  <code>DKIM</code>
  <pre>v=DMARC1; p=none</pre>
  <input type="email" placeholder="name@example.com" />
</template>
<script setup>
const endpoint = { url: '/api/method/suite.mail.send', method: 'POST' }
</script>
"""

        self.assertEqual(self.candidate_texts(source), [])

    def test_ignores_comments_tests_and_explicit_suppression(self):
        source = """
<!-- This comment explains the Add Member dialog. -->
<span>Protocol Status</span> <!-- i18n-audit-ignore -->
// title: 'Internal test title'
"""

        self.assertEqual(self.candidate_texts(source, "Member.test.ts"), [])
        self.assertEqual(self.candidate_texts(source, "Member.vue"), [])

    def test_records_source_line_numbers(self):
        source = "<template>\n  <p>First visible message</p>\n</template>"

        candidates = candidates_from_source(Path("Notice.vue"), source)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].line, 2)
