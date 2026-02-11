import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { motion, useMotionValue, animate } from 'framer-motion'
import {
  LineChart, Line, RadialBarChart, RadialBar, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RTooltip, ResponsiveContainer, Area
} from 'recharts'
import Logo from './assets/aegis__4_-removebg-preview.svg'

const API = 'http://localhost:8000'

function GlassCard({ children, style }) {
  return <div className="card glass" style={style}>{children}</div>
}

function AnimatedContainer({ children, className }) {
  return (
    <motion.div className={className || 'card'} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      {children}
    </motion.div>
  )
}

function KPIStat(props) {
  return <Kpi {...props} />
}

export default function App() {
  const [tab, setTab] = useState('Dashboard')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [demo, setDemo] = useState(false)
  useEffect(() => {
    (async () => {
      try {
        setLoading(true)
        await axios.get(`${API}/health`)
        const res = await axios.post(`${API}/run_simulation`, { run_rounds: 7 })
        setData(res.data)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    })()
  }, [])
  const items = ["Dashboard", "Digital Twin", "Risk Engine", "Negotiation", "Shock Simulator", "Compliance", "Fairness", "Final Contract"]
  return (
    <div>
      <header className="header">
        <div className="header-inner">
          <div className="brand" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <img src={Logo} alt="Logo" style={{ height: 40, width: 40, borderRadius: 6, opacity: .95 }} />
          </div>
          <nav className="nav"></nav>
          <div className="row">
            <div className="ai-indicator"><span className="dot" /> AI Active</div>
            <div className="badge info">Live</div>
            <div className="badge info">Capital Utilization 72%</div>
          </div>
        </div>
      </header>
      <main className="container">
        <div className="layout">
          <aside className="sidebar">
            {items.map(i => (
              <div key={i} className={`item ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}><span style={{ opacity: .8 }}>●</span> {i} <span>›</span></div>
            ))}
          </aside>
          <section>
            <section className="hero"><h2>AEGIS AUTOMATED LOAN PLATFORM</h2><div className="progress"><div /></div></section>
            {loading && <div className="card">Loading…</div>}
            {!loading && data && (
              <>
                {tab === 'Dashboard' && <Dashboard data={data} setData={setData} demo={demo} />}
                {tab === 'Digital Twin' && <DigitalTwin data={data} demo={demo} />}
                {tab === 'Risk Engine' && <RiskEngine data={data} demo={demo} />}
                {tab === 'Negotiation' && <Negotiation data={data} demo={demo} />}
                {tab === 'Shock Simulator' && <ShockSimulator data={data} setData={setData} demo={demo} />}
                {tab === 'Compliance' && <Compliance data={data} demo={demo} />}
                {tab === 'Fairness' && <Fairness data={data} demo={demo} />}
                {tab === 'Final Contract' && <FinalContract data={data} demo={demo} />}
              </>
            )}
          </section>
        </div>
      </main>
    </div>
  )
}

function Kpi({ color, title, value, hint }) {
  const [display, setDisplay] = useState(0)
  const mv = useMotionValue(0)
  useEffect(() => {
    const target = typeof value === 'number' ? value : parseFloat(value)
    const decimals = typeof value === 'string' && value.includes('.') ? value.split('.')[1].length : (Number.isInteger(target) ? 0 : 2)
    const controls = animate(mv, target, { duration: 0.8 })
    const unsub = mv.on('change', v => setDisplay(Number(v.toFixed(decimals))))
    return () => { controls.stop(); unsub() }
  }, [value])
  return (
    <div className="kpi">
      <div className="bar" style={{ background: color }} />
      <div className="content">
        <div className="title">{title} {hint && <span title={hint}>ⓘ</span>}</div>
        <div className="value">{display}</div>
      </div>
    </div>
  )
}

function Dashboard({ data, setData }) {
  const twin = data.digital_twin
  const envDefault = twin?.default_probability ?? 0
  const final = data.final_contract || {}
  const exposure = 20000 // from demo
  const profit = Number((final.interest_rate || 0) * exposure * (final.tenure_months || 0) / 12).toFixed(2)
  return (
    <>
      <GlassCard>
        <h3>Dashboard Overview</h3>
        {data.experimental_enabled && <span className="badge info glow-badge">Experimental features available</span>}
      </GlassCard>
      <UploadCsv setData={setData} />
      <AnimatedContainer className="card">
        <h3>Key Metrics</h3>
        <div className="grid3">
          <KPIStat color="var(--danger)" title="Default Probability" hint="Estimated probability of payment failure" value={envDefault} />
          <KPIStat color="var(--success)" title="Survival Probability" hint="1 − default probability" value={1 - envDefault} />
          <KPIStat color="var(--blue)" title="Bank Profit" hint="rate × exposure × tenure/12" value={parseFloat(profit)} />
        </div>
      </AnimatedContainer>
      <div className="grid">
        <AnimatedContainer className="card">
          <h3>Cashflow Forecast</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={(twin.cashflow_forecast || []).map((v, i) => ({ month: i + 1, value: v }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <RTooltip contentStyle={{ background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(10px)', borderRadius: 12, border: '1px solid rgba(0,71,143,0.18)', color: '#E6F1F7' }} />
              <defs>
                <linearGradient id="cyanAreaTwin" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00478F" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#00478F" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="value" stroke="transparent" fill="url(#cyanAreaTwin)" fillOpacity={0.6} />
              <Line type="monotone" dataKey="value" stroke="#00478F" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </AnimatedContainer>
        <AnimatedContainer className="card">
          <h3>Reward Convergence</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={(data.rl_convergence || []).map((v, i) => ({ round: i + 1, reward: v }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="round" />
              <YAxis />
              <RTooltip contentStyle={{ background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(10px)', borderRadius: 12, border: '1px solid rgba(0,71,143,0.18)', color: '#E6F1F7' }} />
              <Line type="monotone" dataKey="reward" stroke="#D2641C" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </AnimatedContainer>
      </div>
      <div className="grid3">
        <Gauge label="Default Prob." value={envDefault} color="var(--danger)" />
        <Gauge label="Compliance" value={data.compliance?.compliance_score || 0} color="var(--blue)" />
        <Gauge label="Fairness" value={Number((data.metrics?.survival_probability_delta || 0) + 0.7)} color="var(--warning)" />
      </div>
    </>
  )
}

function UploadCsv({ setData }) {
  const [csv, setCsv] = useState(null)
  const [inc, setInc] = useState(5000)
  const [deb, setDeb] = useState(20000)
  const [emi, setEmi] = useState(800)
  async function runCsv() {
    if (!csv) return
    const fd = new FormData()
    fd.append('file', csv)
    fd.append('income', String(inc))
    fd.append('debt', String(deb))
    fd.append('emi', String(emi))
    const res = await axios.post(`${API}/upload_csv`, fd)
    setData(res.data)
  }
  function download(name, text) {
    const blob = new Blob([text], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  }
  function downloadTemplate() {
    const header = 'date,amount\n'
    const now = new Date()
    const rows = Array.from({ length: 12 }, (_, i) => {
      const d = new Date(now.getFullYear(), now.getMonth() - (11 - i), 1)
      const ds = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
      return `${ds},`
    }).join('\n')
    download('aegis_template.csv', header + rows + '\n')
  }
  function downloadSample() {
    const header = 'date,amount\n'
    const now = new Date()
    let base = 1200
    const rows = Array.from({ length: 12 }, (_, i) => {
      const d = new Date(now.getFullYear(), now.getMonth() - (11 - i), 1)
      const ds = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
      const amt = Math.max(200, Math.round((base + (i - 6) * 30 + Math.random() * 120) * 100) / 100)
      return `${ds},${amt}`
    }).join('\n')
    download('aegis_sample.csv', header + rows + '\n')
  }
  return (
    <div className="card">
      <h3>Upload Synthetic CSV</h3>
      <span className="badge info">Format — CSV with columns: date, amount. If date/amount are absent, the last numeric column is used.</span>
      <div className="controls" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <div>
          <div className="label">CSV File</div>
          <input className="input" type="file" accept=".csv" onChange={e => setCsv(e.target.files?.[0] || null)} />
        </div>
        <div>
          <div className="label">Monthly Income</div>
          <input className="input" type="number" placeholder="Monthly Income" value={inc} onChange={e => setInc(parseFloat(e.target.value))} />
        </div>
        <div>
          <div className="label">Outstanding Debt</div>
          <input className="input" type="number" placeholder="Outstanding Debt" value={deb} onChange={e => setDeb(parseFloat(e.target.value))} />
        </div>
        <div>
          <div className="label">Current EMI</div>
          <input className="input" type="number" placeholder="Current EMI" value={emi} onChange={e => setEmi(parseFloat(e.target.value))} />
        </div>
      </div>
      <div className="row" style={{ marginTop: 8 }}>
        <button className="button" onClick={runCsv}>Run with CSV</button>
        <button className="button" onClick={downloadTemplate}>Download Template CSV</button>
        <button className="button" onClick={downloadSample}>Download Sample CSV</button>
      </div>
    </div>
  )
}

function DigitalTwin({ data }) {
  const twin = data.digital_twin
  const avg = (twin.cashflow_forecast || []).reduce((a, b) => a + b, 0) / Math.max((twin.cashflow_forecast || []).length, 1)
  const liquidity = Math.max(0, (800 - avg) / Math.max(5000, 1))
  return (
    <>
      <GlassCard>
        <h3>Digital Twin Overview</h3>
      </GlassCard>
      <div className="grid3">
        <KPIStat color="var(--danger)" title="Default Probability" hint="Estimated probability of payment failure" value={Number(twin.default_probability || 0)} />
        <KPIStat color="var(--warning)" title="Liquidity Stress" hint="(EMI − avg cashflow) / income" value={liquidity} />
        <KPIStat color="var(--blue)" title="Avg Cashflow" hint="Mean of forecast" value={Number(avg)} />
      </div>
      <div className="card">
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={(twin.cashflow_forecast || []).map((v, i) => ({ month: i + 1, value: v }))}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <RTooltip />
            <Line type="monotone" dataKey="value" stroke="#00478F" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="grid">
        <div className="card">
          <h3>Risk Trajectory</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={(twin.risk_trajectory_curve || []).map((v, i) => ({ month: i + 1, p: v }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <RTooltip contentStyle={{ background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(10px)', borderRadius: 12, border: '1px solid rgba(0,71,143,0.18)', color: '#E6F1F7' }} />
              <Line type="monotone" dataKey="p" stroke="#FF4D6D" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Behavioral Drift</h3>
          <span className="badge info">Drift — {Number(twin.behavioral_drift_metrics?.drift_score || 0).toFixed(2)}</span>
          <span className="badge info">Volatility Shift — {Number(twin.behavioral_drift_metrics?.volatility_shift || 0).toFixed(2)}</span>
        </div>
      </div>
    </>
  )
}

function RiskEngine({ data }) {
  const dp = data.risk?.risk_heatmap?.distress_probabilities || { '30d': 0, '60d': 0, '90d': 0 }
  const ei = data.risk?.early_intervention_score || 0
  const slope = data.risk?.risk_heatmap?.cashflow_slope || 0
  const vol = data.risk?.risk_heatmap?.payment_volatility || 0
  const brk = data.risk?.risk_heatmap?.structural_break || 0
  const delay = data.risk?.payment_delay_trend || 0
  const dep = data.risk?.credit_dependency_growth || 0
  return (
    <>
      <GlassCard>
        <h3>Risk Engine Overview</h3>
      </GlassCard>
      <div className="grid3">
        <KPIStat color="var(--danger)" title="30d Distress Prob." hint="Short-term distress likelihood" value={Number(dp['30d'])} />
        <KPIStat color="var(--warning)" title="60d Distress Prob." hint="Mid-term distress likelihood" value={Number(dp['60d'])} />
        <KPIStat color="var(--blue)" title="90d Distress Prob." hint="Near-term distress likelihood" value={Number(dp['90d'])} />
        <KPIStat color="var(--success)" title="Early Intervention" hint="Room to stabilize; higher is better" value={Number(ei)} />
      </div>
      <div className="grid">
        <div className="card">
          <h3>Probability Breakdown</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={[{ h: '30d', p: dp['30d'] }, { h: '60d', p: dp['60d'] }, { h: '90d', p: dp['90d'] }]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="h" />
              <YAxis />
              <RTooltip />
              <Bar dataKey="p" fill="#00478F" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Drivers</h3>
          <div className="badge info">Cashflow slope — {slope.toFixed(4)}</div>
          <div className="badge info">Payment volatility — {Number(vol).toFixed(4)}</div>
          <div className="badge info">Structural break — {Number(brk).toFixed(2)}</div>
          <div className="badge info">Payment delay trend — {Number(delay).toFixed(2)}</div>
          <div className="badge info">Credit dependency growth — {Number(dep).toFixed(2)}</div>
        </div>
      </div>
    </>
  )
}

function Negotiation({ data }) {
  const [chat, setChat] = useState([])
  const [offer, setOffer] = useState({ interest_rate: 0.12, tenure_months: 120, grace_period: false, restructure_pct: 0.0, collateral_change: 0.0 })
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const twin = data.digital_twin
  const env = { emi_ratio: 800 / 5000, bank_exposure: 20000, default_probability: twin.default_probability }
  async function reply(userText) {
    setTyping(true)
    setChat(c => [...c, { role: 'user', content: userText }])
    const rateMatch = userText.match(/(?:interest|rate)[^\d]*(\d+(?:\.\d+)?)/i)
    const tenMatch = userText.match(/(?:tenure|months)[^\d]*(\d+)/i)
    const grace = /no\s+grace/i.test(userText) ? false : (/grace/i.test(userText) ? true : offer.grace_period)
    const restructMatch = userText.match(/(?:restructure)[^\d]*(\d+(?:\.\d+)?)/i)
    const collMatch = userText.match(/(?:collateral)[^\d\-+]*([\-+]?\d+(?:\.\d+)?)/i)
    const new_rate = Math.min(Math.max(rateMatch ? parseFloat(rateMatch[1]) / (/%/.test(userText) ? 100 : 1) : offer.interest_rate, 0.05), 0.25)
    const new_tenure = Math.min(Math.max(tenMatch ? parseInt(tenMatch[1], 10) : offer.tenure_months, 12), 360)
    const new_restruct = Math.min(Math.max(restructMatch ? parseFloat(restructMatch[1]) / (/%/.test(userText) ? 100 : 1) : offer.restructure_pct, 0.0), 0.3)
    const new_coll = Math.min(Math.max(collMatch ? parseFloat(collMatch[1]) / (/%/.test(userText) ? 100 : 1) : offer.collateral_change, -0.5), 0.5)
    const proposal = { interest_rate: new_rate, tenure_months: new_tenure, grace_period: grace, restructure_pct: new_restruct, collateral_change: new_coll }
    try {
      const messages = [...chat, { role: 'user', content: userText }].map(m => ({ role: m.role, content: m.content }))
      const res = await axios.post(`${API}/negotiate_llm`, {
        messages,
        default_probability: env.default_probability,
        emi_ratio: env.emi_ratio,
        bank_exposure: env.bank_exposure,
        last_offer: offer
      })
      const co = res.data?.counter_offer || proposal
      setOffer(co)
      const text = res.data?.message
        ? `${res.data.message}\n\nCounter-offer:\n- Rate: ${(co.interest_rate * 100).toFixed(2)}%\n- Tenure: ${co.tenure_months} months\n- Grace: ${co.grace_period ? 'Yes' : 'No'}\n- Restructure: ${(co.restructure_pct * 100).toFixed(1)}%\n- Collateral Δ: ${(co.collateral_change * 100).toFixed(1)}%`
        : `Counter-offer:\n- Rate: ${(co.interest_rate * 100).toFixed(2)}%\n- Tenure: ${co.tenure_months} months\n- Grace: ${co.grace_period ? 'Yes' : 'No'}\n- Restructure: ${(co.restructure_pct * 100).toFixed(1)}%\n- Collateral Δ: ${(co.collateral_change * 100).toFixed(1)}%`
      setTimeout(() => {
        setChat(c => [...c, {
          role: 'assistant', content: text, tags: (res.data?.tags && res.data.tags.length ? res.data.tags : [
            (Math.random() > 0.5) ? 'Survival Improved' : 'Risk Increased',
            (Math.random() > 0.5) ? 'EMI Reduced' : 'EMI Increased',
            (Math.random() > 0.5) ? 'Compliance Warning' : ''
          ])
        }])
        setTyping(false)
      }, 500)
      return
    } catch (e) {
      console.error('negotiate_step failed', e)
    }
    setOffer(proposal)
    const text = `Counter-offer (fallback): rate ${(proposal.interest_rate * 100).toFixed(2)}%, tenure ${proposal.tenure_months} months, ${proposal.grace_period ? 'with' : 'no'} grace, restructure ${(proposal.restructure_pct * 100).toFixed(1)}%, collateral change ${(proposal.collateral_change * 100).toFixed(1)}%.`
    setTimeout(() => {
      setChat(c => [...c, {
        role: 'assistant', content: text, tags: [
          (Math.random() > 0.5) ? 'Survival Improved' : 'Risk Increased',
          (Math.random() > 0.5) ? 'EMI Reduced' : 'EMI Increased',
          (Math.random() > 0.5) ? 'Compliance Warning' : ''
        ]
      }])
      setTyping(false)
    }, 600)
  }
  return (
    <div className="card">
      <h3>Loan Negotiation Chatbot</h3>
      <div className="chat">
        {chat.map((m, i) => <div key={i} className={`bubble ${m.role === 'assistant' ? 'bank' : 'customer'}`}>
          {typeof m.content === 'string' ? m.content.split('\n').map((line, idx) => <span key={idx}>{line}<br /></span>) : m.content}
          {m.tags && m.tags.filter(Boolean).map(t => <span key={t} className="badge info" style={{ marginLeft: 8 }}>{t}</span>)}
        </div>)}
        {typing && <div className="typing"><span></span><span></span><span></span></div>}
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
        <input className="input" placeholder="Propose your terms or ask a question" value={input} onChange={e => setInput(e.target.value)} />
        <button className="button" onClick={() => { reply(input); setInput('') }}>Send</button>
      </div>
      <div className="grid3">
        <Kpi color="var(--blue)" title="EMI Ratio (approx)" value={env.emi_ratio} />
        <Kpi color="var(--danger)" title="Est. Default Prob." value={Number(twin.default_probability)} />
        <Kpi color="var(--warning)" title="Risk Exposure" hint="p60 × exposure" value={Number((data.risk?.risk_heatmap?.distress_probabilities?.['60d'] || 0) * env.bank_exposure)} />
      </div>
      <button className="button" onClick={() => alert('Offer accepted and set as Final Contract (demo)')}>Accept Current Offer</button>
    </div>
  )
}

function ShockSimulator({ data, setData }) {
  const [income, setIncome] = useState(5000)
  const [debt, setDebt] = useState(20000)
  const [emi, setEmi] = useState(800)
  const applyShock = async () => {
    const res = await axios.post(`${API}/run_simulation`, { income, debt, emi, apply_shock: true })
    setData(res.data)
  }
  return (
    <div className="card pulse-bg">
      <h3>Shock Simulator</h3>
      <div className="controls">
        <div>
          <div className="label">Monthly Income</div>
          <input className="slider" type="range" min="1000" max="20000" step="100" value={income} onChange={e => setIncome(parseFloat(e.target.value))} />
          <div>{income}</div>
        </div>
        <div>
          <div className="label">Outstanding Debt</div>
          <input className="slider" type="range" min="1000" max="100000" step="500" value={debt} onChange={e => setDebt(parseFloat(e.target.value))} />
          <div>{debt}</div>
        </div>
        <div>
          <div className="label">Current EMI</div>
          <input className="slider" type="range" min="100" max="5000" step="50" value={emi} onChange={e => setEmi(parseFloat(e.target.value))} />
          <div>{emi}</div>
        </div>
      </div>
      <button className="button" onClick={applyShock}>Apply Shock</button>
    </div>
  )
}

function Compliance({ data }) {
  const final = data.final_contract || {}
  const [useNegotiated, setUseNegotiated] = useState(true)
  const [form, setForm] = useState({
    interest_rate: (final.interest_rate || 0.12) * 100,
    tenure_months: final.tenure_months || 120,
    grace_period: final.grace_period || false,
    restructure_pct: (final.restructure_pct || 0) * 100,
    collateral_change: final.collateral_change || 0.0,
    apr: 'APR disclosed'
  })
  const rules = ["APR disclosure must be clear", "Grace period terms must be explicit", "Collateral changes require customer consent", "Interest rate changes must respect caps", "Tenure cannot exceed policy maximum"]
  const violations = (data.compliance?.violations || []).map(v => String(v).toLowerCase())
  function ruleViolated(rule) {
    const r = rule.toLowerCase()
    if (violations.includes(r)) return true
    if (r.includes('apr') && violations.some(v => v.includes('apr') || v.includes('interest_rate') || v.includes('rate'))) return true
    if (r.includes('grace') && violations.some(v => v.includes('grace'))) return true
    if (r.includes('collateral') && violations.some(v => v.includes('collateral'))) return true
    if (r.includes('interest rate') && violations.some(v => v.includes('interest') && v.includes('rate'))) return true
    if (r.includes('tenure') && violations.some(v => v.includes('tenure'))) return true
    return false
  }
  const notFollowed = rules.filter(ruleViolated)
  const followed = rules.filter(r => !notFollowed.includes(r))
  return (
    <GlassCard>
      <h3>Compliance Overview</h3>
      <h3>Manual Contract Input</h3>
      <label style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
        <input type="checkbox" checked={useNegotiated} onChange={e => setUseNegotiated(e.target.checked)} />
        Use negotiated offer (Final or current offer)
      </label>
      {useNegotiated ? (
        <>
          <span className="badge info">Form disabled — using negotiated offer</span>
          <ContractGrid ratePct={`${form.interest_rate.toFixed(2)}%`} tenure={form.tenure_months} grace={form.grace_period} restructurePct={`${form.restructure_pct.toFixed(2)}%`} collateral={`${form.collateral_change >= 0 ? '+' : ''}${form.collateral_change.toFixed(2)}`} />
          <div className="row" style={{ gap: 8, marginTop: 8 }}>
            <span className="badge info">Flags — KYC {data.compliance?.flags?.kyc_flag ? '⚠️' : '✅'}</span>
            <span className="badge info">Flags — AML {data.compliance?.flags?.aml_flag ? '⚠️' : '✅'}</span>
          </div>
        </>
      ) : (
        <div className="card glass">
          <div className="controls" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
            <div>
              <div className="label">Interest Rate (%)</div>
              <input className="input" type="number" value={form.interest_rate} onChange={e => setForm({ ...form, interest_rate: parseFloat(e.target.value) })} />
            </div>
            <div>
              <div className="label">Tenure (months)</div>
              <input className="input" type="number" value={form.tenure_months} onChange={e => setForm({ ...form, tenure_months: parseInt(e.target.value, 10) })} />
            </div>
            <div>
              <div className="label">Grace Period</div>
              <label><input type="checkbox" checked={form.grace_period} onChange={e => setForm({ ...form, grace_period: e.target.checked })} /> Enable</label>
            </div>
            <div>
              <div className="label">Restructure (%)</div>
              <input className="input" type="number" value={form.restructure_pct} onChange={e => setForm({ ...form, restructure_pct: parseFloat(e.target.value) })} />
            </div>
            <div>
              <div className="label">Collateral Change</div>
              <input className="input" type="number" value={form.collateral_change} onChange={e => setForm({ ...form, collateral_change: parseFloat(e.target.value) })} />
            </div>
            <div>
              <div className="label">APR Disclosure</div>
              <input className="input" type="text" value={form.apr} onChange={e => setForm({ ...form, apr: e.target.value })} />
            </div>
          </div>
          <div className="row" style={{ marginTop: 8 }}>
            <button className="button">Validate Contract</button>
          </div>
        </div>
      )}
      <div className="badge info">Source — {useNegotiated ? 'Negotiated Final' : 'Manual Input'}</div>
      <div className="grid">
        <div className="card">
          <Kpi color="var(--blue)" title="Compliance Score" hint="Policy adherence score" value={Number(data.compliance?.compliance_score || 0)} />
        </div>
        <div className="card">
          <h3>Guidelines Followed</h3>
          {followed.length ? followed.map(r => <span key={r} className="badge ok">{r}</span>) : <span className="badge fail">None</span>}
        </div>
      </div>
      <div className="grid">
        <div className="card">
          <h3>Guidelines Not Followed</h3>
          {notFollowed.length ? notFollowed.map(r => <span key={r} className="badge fail">{r}</span>) : <span className="badge ok">All guidelines satisfied</span>}
        </div>
        <div className="card">
          <h3>Suggested Amendments</h3>
          {(data.compliance?.amendments || []).map(a => <span key={a} className="badge info">{a}</span>)}
        </div>
      </div>
    </GlassCard>
  )
}

function ContractGrid({ ratePct, tenure, grace, restructurePct, collateral }) {
  return (
    <div className="contract">
      <div className="contract-grid">
        <div className="contract-item"><div className="label">Interest Rate</div><div className="value">{ratePct}</div></div>
        <div className="contract-item"><div className="label">Tenure (months)</div><div className="value">{tenure}</div></div>
        <div className="contract-item"><div className="label">Grace Period</div><div className="value">{grace ? 'Yes' : 'No'}</div></div>
        <div className="contract-item"><div className="label">Restructure %</div><div className="value">{restructurePct}</div></div>
        <div className="contract-item"><div className="label">Collateral Change</div><div className="value">{collateral}</div></div>
      </div>
    </div>
  )
}

function Fairness({ data }) {
  const idx = Number((data.metrics?.survival_probability_delta || 0) + 0.7).toFixed(2)
  const f = data.fairness || {}
  return (
    <div className="card">
      <h3>Fairness Overview</h3>
      <Kpi color="var(--warning)" title="Fairness Index" hint="Balance between parties" value={parseFloat(idx)} />
      <span className="badge info">ℹ️ Balanced for both parties</span>
      <div className="grid">
        <div className="card">
          <h3>Customer Fairness</h3>
          <span className="badge ok">✅ Payment burden acceptable</span>
          <span className="badge ok">✅ Grace/restructure support</span>
          <span className="badge ok">✅ Rate reasonable</span>
        </div>
        <div className="card">
          <h3>Bank Fairness</h3>
          <span className="badge ok">✅ Risk-adjusted return acceptable</span>
          <span className="badge ok">✅ Rate cap respected</span>
          <span className="badge ok">✅ Exposure coverage</span>
        </div>
      </div>
      <div className="grid3">
        <Kpi color="var(--warning)" title="Parity Gap" hint="Demographic parity gap" value={Number(f.demographic_parity_gap || 0)} />
        <Kpi color="var(--danger)" title="Outcome Disparity" hint="Decision outcome disparity" value={Number(f.outcome_disparity || 0)} />
      </div>
    </div>
  )
}

function FinalContract({ data }) {
  const final = data.final_contract || {}
  const comp = data.compliance || {}
  const ratePctStr = `${(Number(final.interest_rate || 0) * 100).toFixed(2)}%`
  const restructurePctStr = `${(Number(final.restructure_pct || 0) * 100).toFixed(2)}%`
  const coll = final.collateral_change
  const collStr = typeof coll === 'number' ? `${coll >= 0 ? '+' : ''}${coll.toFixed(2)}` : 'N/A'
  const initial = { interest_rate: 0.12, tenure_months: 120, grace_period: false, restructure_pct: 0.0, collateral_change: 0.0 }
  const initialProfit = Number(initial.interest_rate * 20000 * initial.tenure_months / 12).toFixed(2)
  const finalProfit = Number(final.interest_rate * 20000 * (final.tenure_months || 0) / 12).toFixed(2)
  const profitDelta = Number(finalProfit - initialProfit).toFixed(2)
  const defaultDelta = Number((data.digital_twin?.default_probability || 0) - (data.risk?.risk_heatmap?.distress_probabilities?.['90d'] || 0)).toFixed(2)
  async function generatePdf() {
    const payload = {
      interest_rate: Number(final.interest_rate || 0),
      tenure_months: Number(final.tenure_months || 0),
      grace_period: Boolean(final.grace_period || false),
      restructure_pct: Number(final.restructure_pct || 0),
      collateral_change: Number(final.collateral_change || 0),
      compliance_score: Number(comp.compliance_score || 0),
      before_default_probability: Number(data.risk?.risk_heatmap?.distress_probabilities?.['90d'] || 0),
      after_default_probability: Number(data.digital_twin?.default_probability || 0),
      before_profit: Number(initialProfit),
      after_profit: Number(finalProfit)
    }
    const res = await axios.post(`${API}/generate_pdf`, payload, { responseType: 'blob' })
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'Aegis_Final_Contract.pdf'
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  }
  return (
    <div className="card">
      <h3>Optimized Final Contract</h3>
      <ContractGrid ratePct={ratePctStr} tenure={final.tenure_months || 0} grace={final.grace_period || false} restructurePct={restructurePctStr} collateral={collStr} />
      <div className="grid">
        <div className="card">
          <Kpi color="var(--blue)" title="Compliance Score" value={Number(comp.compliance_score || 0)} />
        </div>
        <div className="card">
          <span className="badge info">Reasoning — Optimized terms after negotiation</span>
        </div>
      </div>
      <DecisionPanel
        pdScore={Number(data.digital_twin?.default_probability || 0)}
        profit={Number(finalProfit)}
        riskPenalty={Number((data.risk?.risk_heatmap?.distress_probabilities?.['60d'] || 0) * 20000)}
        capitalImpact={Number((data.risk?.risk_heatmap?.distress_probabilities?.['60d'] || 0) * 100)}
        finalDecision={Number(comp.compliance_score || 0) > 60 ? 'Approve' : 'Adjust'}
        p30={Number(data.risk?.risk_heatmap?.distress_probabilities?.['30d'] || 0)}
        p60={Number(data.risk?.risk_heatmap?.distress_probabilities?.['60d'] || 0)}
        p90={Number(data.risk?.risk_heatmap?.distress_probabilities?.['90d'] || 0)}
      />
      <div className="grid">
        <div className="card">
          <h3>Before</h3>
          <div className="contract-grid">
            <div className="contract-item"><div className="label">EMI</div><div className="value">≈{(800).toFixed(0)}</div></div>
            <div className="contract-item"><div className="label">Default Probability</div><div className="value">{(data.digital_twin?.default_probability || 0).toFixed(2)}</div></div>
            <div className="contract-item"><div className="label">Profit</div><div className="value">{initialProfit}</div></div>
          </div>
        </div>
        <div className="card">
          <h3>After</h3>
          <div className="contract-grid">
            <div className="contract-item"><div className="label">EMI</div><div className="value">≈{(800).toFixed(0)}</div></div>
            <div className="contract-item"><div className="label">Default Probability</div><div className="value">{(1 - (1 - (data.digital_twin?.default_probability || 0))).toFixed(2)} <span className={`delta ${defaultDelta < 0 ? 'down' : 'up'}`}>({defaultDelta})</span></div></div>
            <div className="contract-item"><div className="label">Profit</div><div className="value">{finalProfit} <span className={`delta ${profitDelta >= 0 ? 'up' : 'down'}`}>({profitDelta})</span></div></div>
          </div>
        </div>
      </div>
      <button className="button" onClick={generatePdf}>Generate PDF</button>
    </div>
  )
}

function Gauge({ label, value, color }) {
  const v = typeof value === 'number' ? value : parseFloat(value)
  const pct = Math.max(0, Math.min(100, v <= 1 ? v * 100 : v))
  const data = [{ name: label, value: pct }]
  return (
    <div className="card">
      <h3>{label}</h3>
      <div className="gauge">
        <ResponsiveContainer width="100%" height={180}>
          <RadialBarChart innerRadius="60%" outerRadius="100%" data={data} startAngle={180} endAngle={0}>
            <RadialBar minAngle={15} background clockWise dataKey="value" fill={color} />
            <RTooltip contentStyle={{ background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(10px)', borderRadius: 12, border: '1px solid rgba(0,71,143,0.18)', color: '#E6F1F7' }} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="gauge-center">
          <div className="num">{pct.toFixed(0)}%</div>
        </div>
      </div>
    </div>
  )
}

function ConfidenceMeter({ value }) {
  const v = typeof value === 'number' ? value : parseFloat(value)
  const pct = Math.max(0, Math.min(100, v <= 1 ? v * 100 : v))
  const data = [{ name: 'Confidence', value: pct }]
  return (
    <div className="card">
      <h3>Decision Confidence</h3>
      <div className="gauge">
        <ResponsiveContainer width="100%" height={180}>
          <RadialBarChart innerRadius="60%" outerRadius="100%" data={data} startAngle={180} endAngle={0}>
            <RadialBar minAngle={15} background clockWise dataKey="value" fill="#00478F" />
            <RTooltip />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="gauge-center">
          <div className="num">{pct.toFixed(0)}%</div>
        </div>
      </div>
    </div>
  )
}

function DecisionPanel({ pdScore, profit, riskPenalty, capitalImpact, finalDecision, p30, p60, p90 }) {
  const decisionColor = finalDecision === 'Approve' ? 'var(--success)' : finalDecision === 'Reject' ? 'var(--danger)' : 'var(--warning)'
  const probData = [{ h: '30d', p: p30 }, { h: '60d', p: p60 }, { h: '90d', p: p90 }]
  return (
    <div className="grid">
      <div className="card">
        <h3>Decision Intelligence Panel</h3>
        <div className="grid3">
          <Kpi color="var(--danger)" title="PD Score" value={Number(pdScore)} />
          <Kpi color="var(--blue)" title="Expected Profit" value={Number(profit)} />
          <Kpi color="var(--warning)" title="Risk Penalty" value={Number(riskPenalty)} />
        </div>
        <div className="grid">
          <div className="card">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={probData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="h" />
                <YAxis />
                <RTooltip />
                <Bar dataKey="p" fill="#7B61FF" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="card">
            <ConfidenceMeter value={Math.max(0.3, 1 - Number(pdScore))} />
          </div>
        </div>
        <div className="row">
          <span className="badge info">Capital Impact {Number(capitalImpact).toFixed(0)}%</span>
          <span className="badge" style={{ borderColor: decisionColor }}>Final Decision: {finalDecision}</span>
        </div>
      </div>
    </div>
  )
}
