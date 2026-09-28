import json
import unittest
from ala.tutor import validate_practice


class PracticeValidationTests(unittest.TestCase):
    source='Acceptance requires observed behaviour, independent requirements and accountable review.'

    def validate(self, question, **extra):
        return validate_practice(json.dumps({'question':question,'evidence':self.source,**extra}), 'question', self.source, 'fi')

    def test_question_displays_no_private_evidence(self):
        question='Miten generoidun koodin hyväksyminen perustellaan?'
        self.assertEqual(question,self.validate(question))

    def test_rejects_answer_fields_and_explanatory_prose(self):
        for text in ('What is acceptance? Answer: observed behaviour.',
                     'Acceptance requires observed behaviour. What else is required?',
                     'What is acceptance?\nSource: observed behaviour',
                     'What is acceptance? Why?', 'Answer: observed behaviour?'):
            with self.assertRaisesRegex(ValueError,'model_invalid_practice'):
                self.validate(text)
        with self.assertRaises(ValueError): self.validate('What is acceptance?',answer='Observed behaviour')

    def test_rejects_invented_evidence_and_malformed_json(self):
        for raw in ('not JSON',json.dumps({'question':'What is acceptance?','evidence':'Invented evidence absent from the source.'}),
                    json.dumps({'question':'What is acceptance?','evidence':[]}), '[]'):
            with self.assertRaisesRegex(ValueError,'model_invalid_practice'):
                validate_practice(raw,'question',self.source,'en')

    def test_feedback_contains_verifiable_source_quote(self):
        result=validate_practice(json.dumps({'feedback':'Your answer omits accountable review.', 'evidence':self.source}), 'feedback',self.source,'en')
        self.assertIn('Source passage to check [1]',result)
        self.assertIn(self.source,result)

    def test_explicit_abstention(self):
        with self.assertRaisesRegex(ValueError,'source_insufficient'):
            validate_practice('{"question":"","evidence":""}','question',self.source,'en')


if __name__=='__main__':unittest.main()
