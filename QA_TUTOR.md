# Tutor correction and local-model checks — 28 September 2026

This continues the findings in `QA_COURSE_WORKFLOW.md`. Practice generation and
feedback now use a structured response contract rather than displaying raw model
prose without checks.

## Implemented checks

- The model returns a question or feedback field and a private evidence field.
  Extra fields, malformed JSON and wrong types are rejected.
- Evidence must match a contiguous source passage after whitespace normalization
  and contain 20–600 characters. Invented quotations are rejected.
- A question must be one bounded sentence ending in one question mark. Answer
  sections, extra sentences, multiline explanations and citation appendices are
  rejected. Only the question is displayed or saved; its evidence is not exposed
  as an answer hint.
- Feedback includes the validated source passage so the learner can check the
  model's interpretation. It is still formative feedback, not a grade.
- A source is required for both practice tasks. Heading-only/empty sources are
  rejected before contacting a model. The model can abstain when the source is
  insufficient.
- An invalid structured reply gets one retry, then an explicit error. Invalid
  assistant replies are never saved as successful answers. Finnish and English
  messages explain the failure. General chat remains a separate operation.

## Executed validation

- All **33 Python tests** passed, including malformed/answer-leaking replies,
  invented evidence, abstention, empty sources, retry success, retry exhaustion
  and saved-history integrity.
- All 13 ordered real-course integration checkpoints passed with the external
  42-document release corpus and both tested local model configurations.
- `qwen3.5:9b`: the corrected practice sample returned a single question without
  a source explanation. However, its general explanation still included a claim
  contradicting the source, so it was not selected as the active tutor.
- `gpt-oss:20b`: the checked explanation retained the three source requirements;
  the practice question contained no answer; feedback identified the omitted
  accountable-review requirement and quoted the exact source.
- Additional GPT-OSS checks used slide 2 of modules 1, 5 and 9. All three questions
  were relevant and contained no answer. Feedback to an explicitly unanswered
  question referred to a matching source passage. An unrelated geography
  question was declined with `source_insufficient` instead of being graded.
- The running ALA was restarted with these changes and its local model setting
  changed to the already-installed `gpt-oss:20b`. No model download or cloud
  transmission was performed.

Real course text and model response records remain in ignored local `data/`
files, outside version control.

## Limits of these results

Exact evidence matching verifies quotation provenance, not the correctness of
every interpretation. A model can still ask a leading question or misinterpret
valid evidence. The small set of inspected samples is not pedagogical
certification, a comprehensive Finnish-language evaluation, or formal grading
validation. General chat is not subject to the practice JSON contract.
