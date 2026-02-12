
import numpy as np

class CustomerAgent:
    
    def __init__(self, risk_aversion=0.5, seed=42):
        self.risk_aversion = risk_aversion
        self.rng = np.random.default_rng(seed)
    
    def decide(self, loan_amount, interest_rate, duration, pd_score):
        
        interest_cost = loan_amount * interest_rate * duration / 12
        
        utility = loan_amount - interest_cost - self.risk_aversion * pd_score * loan_amount
        
        noise = self.rng.normal(0, loan_amount * 0.05)
        utility += noise
        
        return utility > 0
    
    def get_counteroffer(self, loan_amount, interest_rate):
        
        proposed_rate = interest_rate * self.rng.uniform(0.7, 0.95)
        proposed_amount = loan_amount * self.rng.uniform(1.0, 1.2)
        return proposed_amount, proposed_rate


class RegulatorAgent:
    
    def __init__(self, min_car=0.08, max_portfolio_pd=0.15):
        self.min_car = min_car
        self.max_portfolio_pd = max_portfolio_pd
        self.portfolio_loans = []
        self.total_capital = 0
    
    def update(self, bank_capital, total_exposure, avg_pd):
        
        self.total_capital = bank_capital
        self.total_exposure = total_exposure
        self.avg_pd = avg_pd
    
    def check_constraints(self, bank_capital, new_loan_amount, portfolio_pd):
        
        total_exposure = sum(l['amount'] for l in self.portfolio_loans) + new_loan_amount
        car = bank_capital / (total_exposure + 1e-8)
        
        penalty = 0
        approved = True
        
        if car < self.min_car:
            penalty += (self.min_car - car) * 10000
            approved = False
        
        if portfolio_pd > self.max_portfolio_pd:
            penalty += (portfolio_pd - self.max_portfolio_pd) * 5000
            approved = False
        
        return approved, penalty
    
    def add_loan(self, loan_amount, pd_score):
        self.portfolio_loans.append({'amount': loan_amount, 'pd': pd_score})
    
    def get_portfolio_pd(self):
        if not self.portfolio_loans:
            return 0
        return np.mean([l['pd'] for l in self.portfolio_loans])


def negotiate(bank_action, customer, regulator, env):
    
    int_rate_adj = float(bank_action[0])
    loan_mult = float(bank_action[1])
    approve = float(bank_action[2]) > 0.5
    
    if not approve:
        return False, bank_action, 0
    
    current_rate = env.interest_rate + int_rate_adj
    current_loan = env.outstanding_loan * loan_mult
    
    customer_accepts = customer.decide(
        current_loan, current_rate, 
        env.MAX_MONTHS - env.current_step,
        env.pd_score
    )
    
    if not customer_accepts:
        counter_loan, counter_rate = customer.get_counteroffer(current_loan, current_rate)
        margin = (1 - env.pd_score) * counter_rate - env.pd_score * env.LGD
        if margin > 0:
            current_loan = counter_loan
            current_rate = counter_rate
        else:
            return False, bank_action, 0
    
    portfolio_pd = regulator.get_portfolio_pd()
    reg_approved, penalty = regulator.check_constraints(
        env.bank_capital, current_loan, portfolio_pd
    )
    
    if not reg_approved:
        return False, bank_action, penalty
    
    regulator.add_loan(current_loan, env.pd_score)
    
    adjusted = np.array([
        current_rate - env.interest_rate,
        current_loan / (env.outstanding_loan + 1e-8),
        1.0
    ], dtype=np.float32)
    
    return True, adjusted, penalty


if __name__ == "__main__":
    from src.rl.bank_env import BankLendingEnv
    
    env = BankLendingEnv(seed=42)
    customer = CustomerAgent(seed=42)
    regulator = RegulatorAgent()
    
    obs, _ = env.reset()
    
    print("Multi-Agent Negotiation Test:")
    for i in range(5):
        bank_action = env.action_space.sample()
        approved, final_action, penalty = negotiate(bank_action, customer, regulator, env)
        obs, reward, term, trunc, info = env.step(final_action)
        print(f"  Round {i+1}: Bank proposal -> Approved={approved}, Penalty={penalty:.2f}, Reward={reward:.4f}")
        if term or trunc:
            break
    
    print("Multi-agent test passed!")
