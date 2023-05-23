import spacy

class DualCoreLLM:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def check_coherence(self, text):
        doc = self.nlp(text)

        # Check for semantic coherence
        for token in doc:
            if token.dep_ == 'nsubj' and token.head.pos_ == 'VERB':
                subj = token
                verb = token.head
                for child in verb.children:
                    if child.dep_ == 'dobj':
                        obj = child
                        if obj.text not in [t.text for t in subj.subtree]:
                            return False
        return True

    def check_grammar(self, text):
        doc = self.nlp(text)

        # Check for grammatical correctness
        for sent in doc.sents:
            if sent.root.dep_ == 'ROOT' and sent.root.tag_ != 'VBZ':
                return False
        return True