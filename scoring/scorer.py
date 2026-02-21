class Scorer:
    
    def __init__(self):
        self.weights = {
            'Critical': 25,
            'Major': 5,
            'Minor': 1,
            'Neutral': 0
        }

    def calculate_score(self, errors, base_score=100):
       
        severity_counts = {
            'Critical': 0,
            'Major': 0,
            'Minor': 0,
            'Neutral': 0
        }
        
        category_deductions = {}
        total_deductions = 0

        for error in errors:
            severity = self._parse_severity(error)
            severity_counts[severity] += 1
            
            deduction = self.weights[severity]
            total_deductions += deduction
            
            category = error.subtype
            if category not in category_deductions:
                category_deductions[category] = 0
            category_deductions[category] += deduction

        final_score = max(0, min(100, base_score - total_deductions))

        return {
            'final_score': final_score,
            'total_deductions': total_deductions,
            'error_breakdown': {
                'critical': severity_counts['Critical'],
                'major': severity_counts['Major'],
                'minor': severity_counts['Minor'],
                'neutral': severity_counts['Neutral']
            },
            'category_breakdown': category_deductions
        }

    def _parse_severity(self, error):
        
        explanation = error.explanation.lower() if error.explanation else ""
        
        if 'critical' in explanation:
            return 'Critical'
        elif 'major' in explanation:
            return 'Major'
        elif 'neutral' in explanation:
            return 'Neutral'
        else:
            return 'Minor'

    def get_weights(self):
        """Return current weight scheme."""
        return self.weights.copy()