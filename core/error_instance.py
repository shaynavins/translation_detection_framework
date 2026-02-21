class ErrorInstance:
    #span - what portiion of the text has error 
    # ssybtypee - categroy of eerror 
    
    def __init__(self, span, subtype, confidence, explanation):
        self.span = span
        self.subtype = subtype 
        self.confidence = confidence 
        self.explanation = explanation 

    def __repr__(self):
        return f"[{self.subtype}] {self.span} (conf={self.confidence:.2f})"