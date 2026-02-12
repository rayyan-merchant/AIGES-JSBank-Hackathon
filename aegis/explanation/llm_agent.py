
import json

EXPLANATION_PROMPT_TEMPLATE = 


class ExplanationAgent:
    
    
    def __init__(self, use_llm=False, llm_client=None):
        self.use_llm = use_llm
        self.llm_client = llm_client
    
    def explain(self, pd_score, shap_values, expected_profit, risk_penalty, 
                final_decision, loan_amount=0, interest_rate=0):
        
        if self.use_llm and self.llm_client:
            return self._llm_explain(pd_score, shap_values, expected_profit, 
                                      risk_penalty, final_decision, loan_amount, interest_rate)
        else:
            return self._rule_explain(pd_score, shap_values, expected_profit,
                                       risk_penalty, final_decision, loan_amount, interest_rate)
    
    def _rule_explain(self, pd_score, shap_values, expected_profit, risk_penalty,
                       final_decision, loan_amount, interest_rate):
        
        
        if pd_score < 0.05:
            risk_level = "LOW"
            risk_narrative = f"This applicant has a very low probability of default ({pd_score:.2%}), indicating strong creditworthiness."
        elif pd_score < 0.15:
            risk_level = "MODERATE"
            risk_narrative = f"This applicant has a moderate default probability ({pd_score:.2%}). Standard monitoring recommended."
        else:
            risk_level = "HIGH"
            risk_narrative = f"This applicant has an elevated default probability ({pd_score:.2%}). Enhanced due diligence required."
        
        key_factors = []
        if shap_values:
            sorted_factors = sorted(shap_values, key=lambda x: abs(x.get('shap_value', 0)), reverse=True)[:5]
            for f in sorted_factors:
                direction = "increases" if f.get('shap_value', 0) > 0 else "decreases"
                key_factors.append(f"{f['feature']} {direction} default risk (impact: {f.get('shap_value', 0):.4f})")
        
        net_value = expected_profit - risk_penalty
        if net_value > 0:
            financial = f"Expected net value is positive (${net_value:,.2f}). Interest income of ${loan_amount * interest_rate:,.2f}/year against expected loss of ${pd_score * 0.6 * loan_amount:,.2f}."
        else:
            financial = f"Expected net value is negative (${net_value:,.2f}). Risk-adjusted returns do not justify the exposure."
        
        capital_required = pd_score * loan_amount * 0.08
        regulatory = f"Capital requirement: ${capital_required:,.2f} (Basel IRB). " + \
                     f"Risk weight: {pd_score * 100:.1f}%. " + \
                     ("Compliant with minimum CAR." if capital_required < loan_amount * 0.2 else "Approaching capital limits.")
        
        if final_decision == 'approve' and pd_score > 0.20:
            recommendation = "adjust terms"
        elif final_decision == 'approve':
            recommendation = "approve"
        else:
            recommendation = "reject"
        
        return {
            "risk_summary": risk_narrative,
            "risk_level": risk_level,
            "key_risk_factors": key_factors,
            "financial_impact": financial,
            "regulatory_view": regulatory,
            "final_recommendation": recommendation,
            "metrics": {
                "pd_score": round(pd_score, 4),
                "expected_profit": round(expected_profit, 2),
                "risk_penalty": round(risk_penalty, 2),
                "net_value": round(net_value, 2),
                "loan_amount": round(loan_amount, 2),
                "interest_rate": round(interest_rate, 4)
            }
        }
    
    def _llm_explain(self, pd_score, shap_values, expected_profit, risk_penalty,
                      final_decision, loan_amount, interest_rate):
        
        shap_str = "\n".join([f"- {f['feature']}: {f.get('shap_value', 0):.4f}" for f in (shap_values or [])])
        
        prompt = EXPLANATION_PROMPT_TEMPLATE.format(
            pd_score=pd_score,
            expected_profit=expected_profit,
            risk_penalty=risk_penalty,
            final_decision=final_decision,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            shap_factors=shap_str
        )
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a financial risk analyst."},
                         {"role": "user", "content": prompt}],
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"LLM call failed: {e}. Falling back to rule-based.")
            return self._rule_explain(pd_score, shap_values, expected_profit, 
                                       risk_penalty, final_decision, loan_amount, interest_rate)
    
    def get_prompt_template(self):
        
        return EXPLANATION_PROMPT_TEMPLATE


if __name__ == "__main__":
    agent = ExplanationAgent(use_llm=False)
    
    result = agent.explain(
        pd_score=0.12,
        shap_values=[
            {'feature': 'debt_ratio', 'shap_value': 0.15},
            {'feature': 'revenue_volatility', 'shap_value': 0.10},
            {'feature': 'cash_ratio', 'shap_value': -0.08},
            {'feature': 'employment_years', 'shap_value': -0.05}
        ],
        expected_profit=5000,
        risk_penalty=1200,
        final_decision='approve',
        loan_amount=100000,
        interest_rate=0.08
    )
    
    print(json.dumps(result, indent=2))
    print("\nExplanation Agent test passed!")
