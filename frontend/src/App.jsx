import React,{useEffect,useMemo,useState} from 'react';
import {Routes,Route,NavLink,useNavigate,useLocation,useParams} from 'react-router-dom';
import {Activity,AlertTriangle,ArrowRight,BarChart3,Check,ChevronDown,CircleGauge,Cpu,Database,Flame,Gauge,Layers3,LogOut,Menu,Play,RefreshCw,Settings,ShieldCheck,SlidersHorizontal,Thermometer,UserRound,Wind,Workflow,X,Zap} from 'lucide-react';
import {api} from './api';

const fmt=(v,d=1)=>Number.isFinite(Number(v))?Number(v).toFixed(d):'—';
const pct=v=>`${fmt(Number(v)*100,1)}%`;
const cls=(v,limit=0.7)=>Number(v)>=limit?'danger':Number(v)>=limit*.65?'warn':'good';
const DEMO=[['engineer','Engineer@26120'],['admin','Admin@26120'],['operator','Operator@26120']];
const navItems=[['/dashboard','Dashboard',Gauge],['/wells','Wells',Database],['/digital-twin','Digital Twin',Workflow],['/predictions','Predictions',Cpu],['/optimization','Optimization',SlidersHorizontal],['/alerts','Alerts',AlertTriangle]];

function App(){
 const [auth,setAuth]=useState(!!localStorage.getItem('petrotwin_token')); const [user,setUser]=useState(null); const [health,setHealth]=useState(false); const [mobile,setMobile]=useState(false);
 useEffect(()=>{api.health().then(()=>setHealth(true)).catch(()=>setHealth(false)); if(auth)api.me().then(setUser).catch(()=>setAuth(false));},[auth]);
 const logout=()=>{api.logout();setUser(null);setAuth(false)};
 if(!auth)return <Login onLogin={d=>{setUser(d);setAuth(true)}}/>;
 return <Shell user={user} health={health} logout={logout} mobile={mobile} setMobile={setMobile}><Routes><Route path="/" element={<Dashboard/>}/><Route path="/dashboard" element={<Dashboard/>}/><Route path="/wells" element={<Wells/>}/><Route path="/wells/:id" element={<WellDetail/>}/><Route path="/digital-twin" element={<Twin/>}/><Route path="/predictions" element={<Predictions/>}/><Route path="/optimization" element={<Optimization/>}/><Route path="/alerts" element={<Alerts/>}/><Route path="*" element={<Dashboard/>}/></Routes></Shell>;
}

function Login({onLogin}){const [u,setU]=useState('engineer'),[p,setP]=useState('Engineer@26120'),[loading,setLoading]=useState(false),[err,setErr]=useState(''); const submit=async e=>{e.preventDefault();setLoading(true);setErr('');try{const d=await api.login(u,p);onLogin({username:d.username||u,role:d.role})}catch(x){setErr(x.message)}finally{setLoading(false)}};return <div className="login-page"><div className="login-orb one"/><div className="login-orb two"/><div className="login-card"><div className="brand-large"><div className="logo"><Flame/></div><div><b>PetroTwin AI</b><span>Baghewala Well-to-Surface Digital Twin</span></div></div><div className="login-copy"><span className="eyebrow">SIH 26120 · OIL INDIA LIMITED</span><h1>Engineering intelligence for heavy-oil operations.</h1><p>Model reservoir heating, CSS response, SRP behaviour and production together — then test decisions before approval.</p></div><form onSubmit={submit}><label>Username<input value={u} onChange={e=>setU(e.target.value)} autoComplete="username"/></label><label>Password<input value={p} onChange={e=>setP(e.target.value)} type="password" autoComplete="current-password"/></label>{err&&<div className="error">{err}</div>}<button className="primary wide" disabled={loading}>{loading?<RefreshCw className="spin"/>:<ShieldCheck/>}{loading?'Signing in…':'Enter engineering workspace'}</button></form><div className="demo-box"><span>LOCAL DEMO ACCOUNTS</span>{DEMO.map(([a,b])=><button key={a} onClick={()=>{setU(a);setP(b)}}><b>{a}</b><small>{b}</small></button>)}</div></div></div>}

function Shell({children,user,health,logout,mobile,setMobile}){const loc=useLocation();return <div className="app"><aside className={mobile?'sidebar open':'sidebar'}><div className="brand"><div className="logo"><Flame size={19}/></div><div><b>PetroTwin AI</b><span>Baghewala · SIH 26120</span></div><button className="icon mobile-only" onClick={()=>setMobile(false)}><X/></button></div><div className="nav-title">OPERATIONS</div>{navItems.map(([to,label,I])=><NavLink onClick={()=>setMobile(false)} key={to} to={to} className={({isActive})=>`nav-link ${isActive||loc.pathname.startsWith(to+'/')?'active':''}`}><I/><span>{label}</span></NavLink>)}<div className="sidebar-status"><div className="twin-ring"><Activity/></div><div><b>Digital Twin</b><span>Coupled CSS + SRP</span></div></div><div className="sidebar-bottom"><div className="connection"><i className={health?'online':''}/><span>API</span><b>{health?'ONLINE':'OFFLINE'}</b></div><div className="user-mini"><UserRound/><div><b>{user?.username||'engineer'}</b><span>{user?.role||'engineer'}</span></div><button className="icon" onClick={logout}><LogOut/></button></div></div></aside>{mobile&&<button className="scrim" onClick={()=>setMobile(false)}/>}<main className="main"><header className="topbar"><button className="icon mobile-only" onClick={()=>setMobile(true)}><Menu/></button><div className="crumb"><span>Baghewala Field</span><ArrowRight/><b>{titleFromPath(loc.pathname)}</b></div><div className="top-actions"><div className="api-pill"><i className={health?'online':''}/>{health?'Connected':'API offline'}</div><button className="icon"><Settings/></button></div></header>{children}</main></div>}
function titleFromPath(p){if(p==='/')return 'Command Center';const x=p.split('/').filter(Boolean)[0]||'dashboard';return x.split('-').map(s=>s[0].toUpperCase()+s.slice(1)).join(' ')}

function Page({eyebrow,title,sub,children,actions}){return <div className="page"><div className="page-head"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{sub}</p></div>{actions&&<div className="page-actions">{actions}</div>}</div>{children}</div>}
function Stat({icon:I,label,value,unit,trend,tone='blue'}){return <div className="stat"><div className={`stat-icon ${tone}`}><I/></div><div><span>{label}</span><strong>{value}<small>{unit}</small></strong>{trend&&<em>{trend}</em>}</div></div>}
function Loading(){return <div className="loading"><RefreshCw className="spin"/> Loading engineering state…</div>}
function ErrorBox({message}){return <div className="error panel-error"><AlertTriangle/> {message}</div>}

function useWellState(id){const [data,setData]=useState(null),[err,setErr]=useState(''),[loading,setLoading]=useState(true);const load=()=>{setLoading(true);Promise.all([api.well(id),api.state(id)]).then(([w,s])=>setData({...w,latest_state:s})).catch(e=>setErr(e.message)).finally(()=>setLoading(false))};useEffect(load,[id]);return {data,err,loading,reload:load}}
function uniqueAlerts(items=[]){const seen=new Set();return items.filter(a=>{const key=String(a.id??`${a.alert_type}|${a.severity}|${a.message}`);if(seen.has(key))return false;seen.add(key);return true})}
function Dashboard(){const [wells,setWells]=useState([]),[selected,setSelected]=useState('BGH-023'),[state,setState]=useState(null),[alerts,setAlerts]=useState([]),[err,setErr]=useState('');useEffect(()=>{Promise.all([api.wells(),api.state(selected),api.alerts(selected)]).then(([w,s,a])=>{setWells(w);setState(s);setAlerts(uniqueAlerts(a))}).catch(e=>setErr(e.message))},[selected]);return <Page eyebrow="COMMAND CENTER · BAGHEWALA" title="Well-to-surface operations" sub="A live engineering view of reservoir, CSS, SRP and production state." actions={<select className="well-select" value={selected} onChange={e=>setSelected(e.target.value)}>{wells.map(w=><option key={w.well_id}>{w.well_id}</option>)}</select>}>{err&&<ErrorBox message={err}/>} {!state?<Loading/>:<><div className="stat-grid"><Stat icon={Zap} label="Oil production" value={fmt(state.oil_production_bopd)} unit=" BOPD" trend="Current state"/><Stat icon={Thermometer} label="Reservoir temperature" value={fmt(state.reservoir_temperature_c)} unit=" °C" trend="Thermal state" tone="orange"/><Stat icon={CircleGauge} label="Pump fillage" value={pct(state.pump_fillage)} unit="" trend="SRP loading" tone="green"/><Stat icon={AlertTriangle} label="Water cut" value={pct(state.water_cut)} unit="" trend="Production quality" tone="purple"/></div><div className="dashboard-grid"><div className="panel twin-panel"><div className="panel-head"><div><span className="eyebrow">LIVE DIGITAL TWIN</span><h2>{selected} operating state</h2></div><NavLink to="/digital-twin" className="text-link">Open twin <ArrowRight/></NavLink></div><TwinVisual state={state}/></div><div className="stack"><div className="panel"><div className="panel-head"><h2>Operating envelope</h2><span className="live-dot">LIVE</span></div><MetricBar label="Steam rate" value={state.steam_rate_tpd} max={260} unit=" tpd"/><MetricBar label="Steam temperature" value={state.steam_temperature_c} max={330} unit=" °C"/><MetricBar label="SPM" value={state.spm} max={10} unit=""/><MetricBar label="Rod load" value={state.rod_load_lb} max={14000} unit=" lb"/></div><div className="panel alert-panel"><div className="panel-head"><h2>Active alerts</h2><NavLink to="/alerts" className="text-link">View all</NavLink></div>{alerts.length?alerts.slice(0,3).map(a=><AlertRow key={a.id} a={a}/>):<div className="empty">No active alerts.</div>}</div></div></div></>}</Page>}
function MetricBar({label,value,max,unit}){const w=Math.min(100,Math.max(3,(Number(value)/max)*100));return <div className="metric-bar"><div><span>{label}</span><b>{fmt(value)}{unit}</b></div><div className="bar"><i style={{width:`${w}%`}}/></div></div>}
function TwinVisual({state}){return <div className="twin-visual"><div className="well-column"><div className="surface"><span>Surface</span><b>Production</b></div><div className="pipe"><div className="flow steam"><span>STEAM</span></div><div className="flow oil"><span>OIL</span></div><div className="pump"><CircleGauge/><small>SRP</small></div></div><div className="reservoir"><div className="heat"><Flame/></div><span>HEAVY-OIL RESERVOIR</span><b>{fmt(state.reservoir_temperature_c)} °C</b><small>{fmt(state.oil_viscosity_cp,0)} cP viscosity</small></div></div><div className="twin-side"><div><span>CSS</span><b>{fmt(state.steam_rate_tpd)} tpd</b><small>{fmt(state.steam_temperature_c)} °C steam</small></div><div><span>SRP</span><b>{fmt(state.spm)} SPM</b><small>{pct(state.pump_efficiency)} efficiency</small></div><div><span>ENERGY</span><b>{fmt(state.energy_consumption_kwh)} kWh</b><small>surface demand</small></div></div></div>}
function AlertRow({a}){return <div className="alert-row"><div className={`severity ${a.severity}`}><AlertTriangle/></div><div><b>{a.alert_type.replaceAll('_',' ')}</b><span>{a.message}</span></div><strong>{a.severity}</strong></div>}

function Wells(){const [wells,setWells]=useState(null),[err,setErr]=useState('');useEffect(()=>{api.wells().then(setWells).catch(e=>setErr(e.message))},[]);return <Page eyebrow="ASSET REGISTER" title="Wells" sub="Thirty prototype Baghewala wells available to the digital twin.">{err&&<ErrorBox message={err}/>} {!wells?<Loading/>:<div className="panel table-panel"><div className="table-scroll"><table><thead><tr><th>Well</th><th>Field</th><th>Status</th><th>Temperature</th><th>Oil production</th><th>SPM</th><th>Fillage</th><th></th></tr></thead><tbody>{wells.map(w=>{const s=w.latest_state||{};return <tr key={w.well_id}><td><b>{w.well_id}</b></td><td>{w.field}</td><td><span className="status"><i/> {w.status}</span></td><td>{fmt(s.reservoir_temperature_c)} °C</td><td>{fmt(s.oil_production_bopd)} BOPD</td><td>{fmt(s.spm)}</td><td>{pct(s.pump_fillage)}</td><td><NavLink className="small-btn" to={`/wells/${w.well_id}`}>View</NavLink></td></tr>})}</tbody></table></div></div>}</Page>}

function WellDetail(){const {id}=useParams();const {data,err,loading,reload}=useWellState(id);return <Page eyebrow="WELL DETAIL" title={id} sub="Current state and engineering parameters." actions={<button className="secondary" onClick={reload}><RefreshCw/> Refresh</button>}>{err&&<ErrorBox message={err}/>} {loading?<Loading/>:data&&<><div className="stat-grid"><Stat icon={Zap} label="Oil production" value={fmt(data.latest_state.oil_production_bopd)} unit=" BOPD"/><Stat icon={Thermometer} label="Reservoir temperature" value={fmt(data.latest_state.reservoir_temperature_c)} unit=" °C" tone="orange"/><Stat icon={Gauge} label="Pump efficiency" value={pct(data.latest_state.pump_efficiency)} tone="green"/><Stat icon={Flame} label="Steam rate" value={fmt(data.latest_state.steam_rate_tpd)} unit=" tpd" tone="purple"/></div><div className="two-col"><div className="panel"><div className="panel-head"><h2>Reservoir & CSS</h2></div><DetailGrid state={data.latest_state} fields={['reservoir_pressure_bar','reservoir_temperature_c','oil_viscosity_cp','steam_rate_tpd','steam_temperature_c','steam_pressure_bar','steam_quality','soak_time_hours']}/></div><div className="panel"><div className="panel-head"><h2>SRP & surface</h2></div><DetailGrid state={data.latest_state} fields={['spm','stroke_length_m','vfd_frequency_hz','pump_efficiency','pump_fillage','rod_load_lb','water_cut','energy_consumption_kwh']}/></div></div></>}</Page>}
function DetailGrid({state,fields}){const labels={reservoir_pressure_bar:'Reservoir pressure',reservoir_temperature_c:'Reservoir temperature',oil_viscosity_cp:'Oil viscosity',steam_rate_tpd:'Steam rate',steam_temperature_c:'Steam temperature',steam_pressure_bar:'Steam pressure',steam_quality:'Steam quality',soak_time_hours:'Soak time',spm:'SPM',stroke_length_m:'Stroke length',vfd_frequency_hz:'VFD frequency',pump_efficiency:'Pump efficiency',pump_fillage:'Pump fillage',rod_load_lb:'Rod load',water_cut:'Water cut',energy_consumption_kwh:'Energy consumption'};return <div className="detail-grid">{fields.map(f=><div key={f}><span>{labels[f]}</span><b>{fmt(state[f])}{f.includes('temperature')?' °C':f.includes('pressure')?' bar':f.includes('viscosity')?' cP':f.includes('rate')?' tpd':f.includes('hours')?' h':f==='water_cut'||f.includes('efficiency')||f.includes('fillage')?'':f.includes('energy')?' kWh':''}</b></div>)}</div>}

function Twin(){
 const [wells,setWells]=useState([]),[id,setId]=useState('BGH-023'),[state,setState]=useState(null),[history,setHistory]=useState([]),[result,setResult]=useState(null),[loading,setLoading]=useState(false),[err,setErr]=useState('');
 const [s,setS]=useState({steam_rate:195,steam_temperature:315,soak_time:54,spm:7,stroke_length:2.7});
 const load=async(wellId)=>{
   setErr('');
   try{
     const [nextState,nextHistory]=await Promise.all([api.state(wellId),api.history(wellId,90)]);
     setState(nextState);
     setHistory(Array.isArray(nextHistory)?nextHistory:[]);
   }catch(e){setErr(e.message)}
 };
 useEffect(()=>{
   api.wells().then(setWells).catch(e=>setErr(e.message));
   load(id);
 },[id]);
 const run=async()=>{
   setLoading(true);setErr('');
   try{setResult(await api.simulate(id,s))}
   catch(e){setErr(e.message)}
   finally{setLoading(false)}
 };
 const latest=history.length?history[history.length-1]:{};
 return <Page
   eyebrow="DIGITAL TWIN"
   title="Well Digital Twin"
   sub="Live reservoir, CSS, SRP and surface state with a coupled CSS-cycle what-if simulation."
   actions={<div className="inline-actions"><select className="well-select" value={id} onChange={e=>{setId(e.target.value);setResult(null)}}>{wells.map(w=><option key={w.well_id}>{w.well_id}</option>)}</select><button className="secondary" onClick={()=>load(id)} disabled={loading}><RefreshCw/> Refresh state</button></div>}
 >
   {err&&<ErrorBox message={err}/>}
   {!state?<Loading/>:<>
     <div className="twin-hero">
       <div>
         <span className="eyebrow">WELL {id} · SYNTHETIC PROTOTYPE STATE</span>
         <h2>Well-to-surface operating model</h2>
         <p>One engineering state connecting reservoir heating, CSS response, SRP loading and surface production.</p>
       </div>
       <div className="twin-hero-badges"><span className="status"><i/> ONLINE</span><span className="cycle-badge">CSS {latest.cycle_id||'CURRENT'}</span></div>
     </div>

     <div className="twin-state-grid">
       <TwinStateCard title="Reservoir" icon={Thermometer} items={[
         ['Temperature',`${fmt(state.reservoir_temperature_c)} °C`],
         ['Pressure',`${fmt(state.reservoir_pressure_bar)} bar`],
         ['Oil viscosity',`${fmt(state.oil_viscosity_cp,0)} cP`],
         ['Well depth',latest.well_depth_m?`${fmt(latest.well_depth_m,0)} m`:'—'],
         ['API gravity',latest.api_gravity_deg?`${fmt(latest.api_gravity_deg,1)} °API`:'—']
       ]}/>
       <TwinStateCard title="CSS / Steam" icon={Flame} items={[
         ['Steam rate',`${fmt(state.steam_rate_tpd)} t/day`],
         ['Steam temperature',`${fmt(state.steam_temperature_c)} °C`],
         ['Steam pressure',`${fmt(state.steam_pressure_bar)} bar`],
         ['Steam quality',pct(state.steam_quality)],
         ['Injection duration',latest.injection_duration_days?`${fmt(latest.injection_duration_days)} days`:'—'],
         ['Soak time',`${fmt(state.soak_time_hours)} h`]
       ]}/>
       <TwinStateCard title="SRP / Mechanical" icon={CircleGauge} items={[
         ['SPM',fmt(state.spm)],
         ['Stroke length',`${fmt(state.stroke_length_m)} m`],
         ['VFD frequency',`${fmt(state.vfd_frequency_hz)} Hz`],
         ['Pump efficiency',pct(state.pump_efficiency)],
         ['Pump fillage',pct(state.pump_fillage)],
         ['Rod load',`${fmt(state.rod_load_lb,0)} lb`]
       ]}/>
       <TwinStateCard title="Surface / Production" icon={Activity} items={[
         ['Oil production',`${fmt(state.oil_production_bopd)} BOPD`],
         ['Water cut',pct(state.water_cut)],
         ['Energy',`${fmt(state.energy_consumption_kwh)} kWh/day`],
         ['SOR',fmt(latest.steam_oil_ratio)],
         ['Production phase',latest.css_phase?latest.css_phase.replaceAll('_',' '):'—'],
         ['Production duration',latest.production_duration_days?`${fmt(latest.production_duration_days)} days`:'—']
       ]}/>
     </div>

     <div className="css-cycle panel">
       <div className="panel-head">
         <div><span className="eyebrow">CSS CYCLE</span><h2>Injection → Soaking → Production</h2></div>
         <span className="cycle-current">{latest.css_phase?latest.css_phase.toUpperCase():'CURRENT'}</span>
       </div>
       <div className="cycle-track">
         <CssStage active={latest.css_phase==='injection'} icon={Wind} title="Steam injection" value={`${fmt(state.steam_rate_tpd)} t/day`} detail={`${fmt(state.steam_temperature_c)} °C · ${pct(state.steam_quality)} quality`}/>
         <div className="cycle-arrow"><ArrowRight/></div>
         <CssStage active={latest.css_phase==='soaking'} icon={Flame} title="Soaking" value={`${fmt(state.soak_time_hours)} hours`} detail="Heat diffuses into the heavy-oil zone"/>
         <div className="cycle-arrow"><ArrowRight/></div>
         <CssStage active={latest.css_phase==='production'} icon={Zap} title="Production" value={`${fmt(state.oil_production_bopd)} BOPD`} detail={`${pct(state.water_cut)} water cut · SRP ${fmt(state.spm)} SPM`}/>
       </div>
       <div className="causal-chain">
         <span>Steam</span><ArrowRight/><span>Thermal response</span><ArrowRight/><span>Viscosity ↓</span><ArrowRight/><span>Mobility ↑</span><ArrowRight/><span>SRP response</span><ArrowRight/><span>Production</span>
       </div>
     </div>

     <div className="twin-history-grid">
       <div className="panel">
         <div className="panel-head"><div><span className="eyebrow">PRODUCTION HISTORY</span><h2>Recent well response</h2></div><span className="history-count">{history.length} observations</span></div>
         <HistoryChart history={history}/>
       </div>
       <div className="panel twin-visual-panel">
         <div className="panel-head"><div><span className="eyebrow">WELL CROSS-SECTION</span><h2>Current twin state</h2></div><span className="live-dot">LIVE</span></div>
         <TwinVisual state={state}/>
       </div>
     </div>

     <div className="sim-grid twin-sim-section">
       <div className="panel controls">
         <div className="panel-head"><div><span className="eyebrow">WHAT-IF ENGINE</span><h2>Change operating conditions</h2></div><button className="primary" onClick={run} disabled={loading}><Play/>{loading?'Running…':'Run digital twin'}</button></div>
         {[['steam_rate','Steam rate','t/day',120,240,1],['steam_temperature','Steam temperature','°C',280,325,1],['soak_time','Soak time','h',30,72,1],['spm','SPM','',4,10,.1],['stroke_length','Stroke length','m',2,3.2,.05]].map(([k,l,u,min,max,step])=><label className="slider" key={k}><div><span>{l}</span><b>{fmt(s[k])} {u}</b></div><input type="range" min={min} max={max} step={step} value={s[k]} onChange={e=>setS({...s,[k]:Number(e.target.value)})}/><div className="range"><span>{min}</span><span>{max}</span></div></label>)}
         <div className="scenario-note"><Zap/><span><b>Coupled response:</b> CSS changes influence thermal state and viscosity; SRP changes influence fillage, rod loading and mechanical risk.</span></div>
       </div>
       <div className="panel">
         <div className="panel-head"><div><span className="eyebrow">TWIN OUTPUT</span><h2>{result?'Simulated future state':'Current vs simulated'}</h2></div>{result&&<span className="status approved">SIMULATED</span>}</div>
         <Comparison state={state} result={result?.result}/>
       </div>
     </div>
   </>}
 </Page>
}

function TwinStateCard({title,icon:I,items}){
 return <div className="twin-state-card"><div className="twin-state-title"><div className="state-icon"><I/></div><div><span>SUBSYSTEM</span><h3>{title}</h3></div></div><div className="twin-state-items">{items.map(([label,value])=><div key={label}><span>{label}</span><b>{value}</b></div>)}</div></div>
}

function CssStage({active,icon:I,title,value,detail}){
 return <div className={`css-stage ${active?'active':''}`}><div className="css-stage-icon"><I/></div><div><span>{active?'ACTIVE STAGE':'CSS PHASE'}</span><h3>{title}</h3><b>{value}</b><small>{detail}</small></div></div>
}

function HistoryChart({history=[]}){
 const points=history.filter(x=>Number.isFinite(Number(x.oil_production_bopd))).slice(-30);
 if(points.length<2)return <div className="history-empty">Production history is not available for charting.</div>;
 const vals=points.map(x=>Number(x.oil_production_bopd)), min=Math.min(...vals),max=Math.max(...vals),range=Math.max(max-min,.01);
 const W=760,H=220,P=28;
 const xy=(v,i)=>[P+(i/(points.length-1))*(W-P*2),H-P-((v-min)/range)*(H-P*2)];
 const path=points.map((x,i)=>{const [px,py]=xy(Number(x.oil_production_bopd),i);return `${i?'L':'M'} ${px.toFixed(1)} ${py.toFixed(1)}`}).join(' ');
 const latest=points[points.length-1], first=points[0];
 return <div className="history-chart"><div className="history-legend"><span><i/> Oil production · BOPD</span><b>{fmt(latest.oil_production_bopd)} BOPD current</b></div><svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Oil production history"><line x1={P} y1={H-P} x2={W-P} y2={H-P} className="chart-axis"/><line x1={P} y1={P} x2={P} y2={H-P} className="chart-axis"/><path d={path} className="chart-line"/>{points.map((x,i)=>{const [px,py]=xy(Number(x.oil_production_bopd),i);return i===points.length-1?<circle key={i} cx={px} cy={py} r="4" className="chart-point"/>:null})}</svg><div className="history-labels"><span>{String(first.date||'').slice(0,10)}</span><span>{String(latest.date||'').slice(0,10)}</span></div></div>
}
function Comparison({ state, result }) {
  const current = {
    production: Number(state?.oil_production_bopd),
    temperature: Number(state?.reservoir_temperature_c),
    viscosity: Number(state?.oil_viscosity_cp),
    sor: null,
    energy: Number(state?.energy_consumption_kwh),
    failure: null,
    fillage: Number(state?.pump_fillage),
    rodLoad: Number(state?.rod_load_lb),
    efficiency: Number(state?.pump_efficiency),
  };

  const simulated = result
    ? {
        production: Number(result.production),
        temperature: Number(result.temperature_24h),
        viscosity: Number(result.viscosity_cp),
        sor: Number(result.sor),
        energy: Number(result.energy),
        failure: Number(result.failure_risk),
        fillage: Number(result.pump_fillage),
        rodLoad: Number(result.rod_load_lb),
        efficiency: Number(result.pump_efficiency),
      }
    : null;

  const fmtValue = (value, suffix = "") =>
    Number.isFinite(value) ? `${value.toFixed(1)}${suffix}` : "—";

  const fmtPercent = (value) =>
    Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "—";

  const metrics = [
    {
      label: "Oil production",
      current: fmtValue(current.production, " BOPD"),
      simulated: simulated ? fmtValue(simulated.production, " BOPD") : "—",
    },
    {
      label: "Reservoir temperature",
      current: fmtValue(current.temperature, " °C"),
      simulated: simulated ? fmtValue(simulated.temperature, " °C") : "—",
    },
    {
      label: "Oil viscosity",
      current: fmtValue(current.viscosity, " cP"),
      simulated: simulated ? fmtValue(simulated.viscosity, " cP") : "—",
    },
    {
      label: "Steam-oil ratio",
      current: current.sor === null ? "—" : fmtValue(current.sor),
      simulated: simulated ? fmtValue(simulated.sor) : "—",
    },
    {
      label: "Energy consumption",
      current: fmtValue(current.energy, " kWh"),
      simulated: simulated ? fmtValue(simulated.energy, " kWh") : "—",
    },
    {
      label: "Failure risk",
      current: "—",
      simulated: simulated ? fmtPercent(simulated.failure) : "—",
    },
    {
      label: "Pump fillage",
      current: fmtPercent(current.fillage),
      simulated: simulated ? fmtPercent(simulated.fillage) : "—",
    },
    {
      label: "Rod load",
      current: fmtValue(current.rodLoad, " lb"),
      simulated: simulated ? fmtValue(simulated.rodLoad, " lb") : "—",
    },
    {
      label: "Pump efficiency",
      current: fmtPercent(current.efficiency),
      simulated: simulated ? fmtPercent(simulated.efficiency) : "—",
    },
  ];

  return (
    <div className="comparison">
      <div className="comparison-head">
        <div>
          <span className="eyebrow">SCENARIO RESPONSE</span>
          <h3>Current vs simulated</h3>
        </div>

        {result ? (
          <span className="status approved">TWIN RESPONSE READY</span>
        ) : (
          <span className="status">RUN A SCENARIO</span>
        )}
      </div>

      <div className="comparison-table">
        <div className="comparison-row comparison-header">
          <span>Metric</span>
          <span>Current</span>
          <span>Simulated</span>
        </div>

        {metrics.map((metric) => (
          <div className="comparison-row" key={metric.label}>
            <span>{metric.label}</span>
            <strong>{metric.current}</strong>
            <strong className={result ? "comparison-result" : ""}>
              {metric.simulated}
            </strong>
          </div>
        ))}
      </div>

      {!result && (
        <div className="comparison-empty">
          <span>Adjust CSS + SRP parameters and run the Digital Twin.</span>
        </div>
      )}
    </div>
  );
}
function Predictions(){const [id,setId]=useState('BGH-023'),[wells,setWells]=useState([]),[data,setData]=useState(null),[models,setModels]=useState(null),[loading,setLoading]=useState(false),[err,setErr]=useState('');useEffect(()=>{api.wells().then(setWells);api.modelStatus().then(setModels).catch(e=>setErr(e.message))},[]);const run=async()=>{setLoading(true);try{const [p,t,f]=await Promise.all([api.production(id),api.temperature(id),api.failure(id)]);setData({p,t,f})}catch(e){setErr(e.message)}finally{setLoading(false)}};return <Page eyebrow="MODEL INTELLIGENCE" title="Predictions" sub="Inference from the trained SIH 26120 model artifacts; no retraining occurs in the frontend." actions={<div className="inline-actions"><select className="well-select" value={id} onChange={e=>setId(e.target.value)}>{wells.map(w=><option key={w.well_id}>{w.well_id}</option>)}</select><button className="primary" onClick={run} disabled={loading}><Cpu/>{loading?'Predicting…':'Run predictions'}</button></div>}>{err&&<ErrorBox message={err}/>}<div className="model-grid">{models&&[['Production',models.production,'MAE / RMSE / R²'],['Temperature',models.temperature,'MAE / RMSE / R²'],['Failure',models.failure,'Precision / Recall / PR-AUC']].map(([n,m,desc])=><div className="model-card" key={n}><div className="model-icon"><Cpu/></div><span>{n}</span><b>{m.selected_model}</b><small>{desc}</small><em>{n==='Failure'?'Early-warning signal':'Regression model'}</em></div>)}</div>{data&&<div className="stat-grid"><Stat icon={Zap} label="24h production prediction" value={fmt(data.p?.prediction??data.p?.value??data.p?.predicted_value)} unit=" BOPD"/><Stat icon={Thermometer} label="24h temperature prediction" value={fmt(data.t?.prediction??data.t?.value??data.t?.predicted_value)} unit=" °C" tone="orange"/><Stat icon={AlertTriangle} label="7d failure probability" value={pct(data.f?.prediction??data.f?.probability??data.f?.value??0)} tone="red"/></div>}</Page>}

function Optimization(){const [id,setId]=useState('BGH-023'),[wells,setWells]=useState([]),[opt,setOpt]=useState(null),[rec,setRec]=useState(null),[loading,setLoading]=useState(false),[decision,setDecision]=useState(''),[note,setNote]=useState('Approved for prototype simulation and engineering review.'),[err,setErr]=useState('');useEffect(()=>{api.wells().then(setWells);loadRec('BGH-023')},[]);const loadRec=async(x=id)=>{try{setRec(await api.latestRecommendation(x))}catch{setRec(null)}};const run=async()=>{setLoading(true);setErr('');try{const o=await api.optimize(id);setOpt(o);setRec(await api.latestRecommendation(id));}catch(e){setErr(e.message)}finally{setLoading(false)}};const decide=async status=>{if(!rec||loading||['approved','rejected'].includes(rec.status))return;setLoading(true);setErr('');try{const r=await api.decision(rec.id,status,note);setDecision(r.status);setRec(await api.latestRecommendation(id))}catch(e){setErr(e.message)}finally{setLoading(false)}};return <Page eyebrow="DECISION OPTIMIZATION" title="Constrained operating strategies" sub="Compare production, efficiency and equipment-risk trade-offs before engineer approval." actions={<div className="inline-actions"><select className="well-select" value={id} onChange={e=>{setId(e.target.value);setOpt(null);loadRec(e.target.value)}}>{wells.map(w=><option key={w.well_id}>{w.well_id}</option>)}</select><button className="primary" onClick={run} disabled={loading}><SlidersHorizontal/>{loading?'Optimizing…':'Run optimization'}</button></div>}>{err&&<ErrorBox message={err}/>} {opt&&<div className="strategy-grid">{opt.strategies.map(x=><Strategy key={x.name} s={x}/>)}</div>} {rec&&<div className="panel recommendation"><div className="panel-head"><div><span className="eyebrow">ENGINEER REVIEW</span><h2>Recommended strategy · {rec.strategy_name}</h2></div><span className={`status ${rec.status}`}>{rec.status}</span></div><div className="rec-grid"><div><span>Expected production</span><b>{fmt(rec.result.production)} BOPD</b></div><div><span>Expected SOR</span><b>{fmt(rec.result.sor)}</b></div><div><span>Scenario failure risk</span><b>{pct(rec.result.failure_risk)}</b></div><div><span>Pump efficiency</span><b>{pct(rec.result.pump_efficiency)}</b></div></div><div className="changes">{rec.explanation?.parameter_changes?.map(x=><span key={x.parameter}>{x.parameter.replaceAll('_',' ')} <b>{x.change>0?'+':''}{fmt(x.change)}</b></span>)}</div><div className="approval"><textarea value={note} onChange={e=>setNote(e.target.value)} placeholder="Decision note" disabled={loading||['approved','rejected'].includes(rec.status)}/><div><button className="secondary" onClick={()=>decide('modified')} disabled={loading||['approved','rejected'].includes(rec.status)}>Modify</button><button className="danger-btn" onClick={()=>decide('rejected')} disabled={loading||['approved','rejected'].includes(rec.status)}>Reject</button><button className="approve" onClick={()=>decide('approved')} disabled={loading||['approved','rejected'].includes(rec.status)}><Check/> {loading?'Saving…':rec.status==='approved'?'Approved':'Approve'}</button></div></div><small className="human-note">Human approval required. Approval records the engineering decision; it does not directly control field equipment.</small></div>}</Page>}
function Strategy({s}){return <div className="strategy"><div className="strategy-top"><span>{s.name}</span><small>score {fmt(s.score,2)}</small></div><div className="strategy-main"><b>{fmt(s.result.production)}</b><span>BOPD</span></div><div className="strategy-stats"><span>SOR <b>{fmt(s.result.sor)}</b></span><span>Energy <b>{fmt(s.result.energy)} kWh</b></span><span>Risk <b>{pct(s.result.failure_risk)}</b></span><span>Fillage <b>{pct(s.result.pump_fillage)}</b></span></div><div className="scenario-line"><span>Steam {fmt(s.scenario.steam_rate_tpd)} tpd</span><span>SPM {fmt(s.scenario.spm)}</span><span>Soak {fmt(s.scenario.soak_time_hours)} h</span></div></div>}

function Alerts(){const [id,setId]=useState('BGH-023'),[wells,setWells]=useState([]),[alerts,setAlerts]=useState(null),[err,setErr]=useState('');useEffect(()=>{api.wells().then(setWells);api.alerts(id).then(a=>setAlerts(uniqueAlerts(a))).catch(e=>setErr(e.message))},[id]);return <Page eyebrow="RISK MONITORING" title="Alerts" sub="Early-warning signals from the current well and prediction pipeline." actions={<select className="well-select" value={id} onChange={e=>{setId(e.target.value);api.alerts(e.target.value).then(a=>setAlerts(uniqueAlerts(a)))}}>{wells.map(w=><option key={w.well_id}>{w.well_id}</option>)}</select>}>{err&&<ErrorBox message={err}/>}<div className="alert-summary"><Stat icon={AlertTriangle} label="Open alerts" value={alerts?.length??'—'} tone="red"/><div className="panel alert-disclaimer"><ShieldCheck/><div><b>Engineering interpretation</b><span>Failure alerts are early-warning signals, not certainty. Digital Twin scenario risk and 7-day failure probability are displayed separately.</span></div></div></div><div className="panel page-alerts">{alerts?.length?alerts.map(a=><AlertRow key={a.id} a={a}/>):alerts?<div className="empty">No alerts for {id}.</div>:<Loading/>}</div></Page>}

export default App;
