import json

class ComplianceAgent:
    def __init__(self):
        self.embedder = None
        self.faiss = None
        self.rules = [
            "APR disclosure must be clear",
            "Grace period terms must be explicit",
            "Collateral changes require customer consent",
            "Interest rate changes must respect caps",
            "Tenure cannot exceed policy maximum",
        ]
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            self.embedder = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L6-v2")
            self.faiss = faiss
            X = self.embedder.encode(self.rules)
            index = faiss.IndexFlatIP(X.shape[1])
            index.add(X.astype("float32"))
            self.index = index
        except Exception:
            self.index = None

    def validate(self, contract_json):
        text = json.dumps(contract_json, sort_keys=True)
        violations = []
        score = 100.0
        if self.index is not None and self.embedder is not None:
            q = self.embedder.encode([text]).astype("float32")
            D, I = self.index.search(q, 3)
            refs = [self.rules[i] for i in I[0]]
            score = float(min(100.0, 70.0 + 5.0 * float(D[0].mean())))
            for r in self.rules:
                if r not in refs and any(k in text.lower() for k in ["rate", "tenure", "grace", "collateral"]):
                    violations.append(r)
        else:
            checks = {
                "apr": "apr" in text.lower() or "interest_rate" in text.lower(),
                "grace": "grace" in text.lower(),
                "collateral": "collateral" in text.lower(),
                "tenure": "tenure" in text.lower(),
            }
            score = float(60.0 + 10.0 * sum(1 for v in checks.values() if v))
            for k, v in checks.items():
                if not v:
                    violations.append(f"missing {k}")
        rate = None
        tenure = None
        try:
            rate = float(contract_json.get("interest_rate", None))
        except Exception:
            rate = None
        try:
            tenure = int(contract_json.get("tenure_months", None))
        except Exception:
            tenure = None
        rate_cap = 0.20
        max_tenure = 360
        if rate is not None and rate > rate_cap:
            violations.append("interest rate cap exceeded")
            score -= 8.0
        if tenure is not None and tenure > max_tenure:
            violations.append("tenure exceeds policy maximum")
            score -= 6.0
        amendments = []
        for v in violations:
            if "APR" in v or "apr" in v or "interest_rate" in text:
                amendments.append("add APR disclosure clause")
            elif "grace" in v:
                amendments.append("define grace period conditions")
            elif "collateral" in v:
                amendments.append("include collateral change consent section")
            elif "tenure" in v:
                amendments.append("state maximum tenure and policy reference")
        flags = {"kyc_flag": False, "aml_flag": False}
        return {"compliance_score": float(max(0.0, min(score, 100.0))), "violations": violations, "amendments": amendments, "flags": flags, "reasoning": "rule matching and vector search"}
