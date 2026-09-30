const API_BASE=(import.meta.env.VITE_API_BASE_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
let token=localStorage.getItem('petrotwin_token')||'';
async function request(path,options={}){
  const headers={'Content-Type':'application/json',...(options.headers||{})};
  if(token) headers.Authorization=`Bearer ${token}`;
  const res=await fetch(`${API_BASE}${path}`,{...options,headers});
  const raw=await res.text();
  let data=null; try{data=raw?JSON.parse(raw):null}catch{data=raw;}
  if(!res.ok){if(res.status===401){token='';localStorage.removeItem('petrotwin_token');} const msg=data?.detail?.[0]?.msg||data?.detail||data?.message||`${res.status} ${res.statusText}`; throw new Error(typeof msg==='string'?msg:JSON.stringify(msg));}
  return data;
}
export const api={
 base:API_BASE,
 health:()=>request('/health'),
 login:async(username,password)=>{const data=await request('/api/v1/auth/login',{method:'POST',body:JSON.stringify({username,password})}); token=data.access_token; localStorage.setItem('petrotwin_token',token); return data;},
 me:()=>request('/api/v1/auth/me'),
 logout:()=>{token='';localStorage.removeItem('petrotwin_token');},
 wells:()=>request('/api/v1/wells'),
 well:(id)=>request(`/api/v1/wells/${encodeURIComponent(id)}`),
 state:(id)=>request(`/api/v1/wells/${encodeURIComponent(id)}/state`),
 history:(id)=>request(`/api/v1/wells/${encodeURIComponent(id)}/history`),
 modelStatus:()=>request('/api/v1/predict/model/status'),
 production:(id,scenario={})=>request('/api/v1/predict/production',{method:'POST',body:JSON.stringify({well_id:id,scenario})}),
 temperature:(id,scenario={})=>request('/api/v1/predict/temperature',{method:'POST',body:JSON.stringify({well_id:id,scenario})}),
 failure:(id,scenario={})=>request('/api/v1/predict/failure',{method:'POST',body:JSON.stringify({well_id:id,scenario})}),
 simulate:(id,scenario={})=>request('/api/v1/simulation',{method:'POST',body:JSON.stringify({well_id:id,scenario})}),
 optimize:(id)=>request('/api/v1/optimization',{method:'POST',body:JSON.stringify({well_id:id})}),
 latestRecommendation:(id)=>request(`/api/v1/optimization/${encodeURIComponent(id)}/recommendation`),
 recommendations:(id)=>request(`/api/v1/recommendations/${encodeURIComponent(id)}`),
 decision:(id,status,decision_note)=>request(`/api/v1/optimization/recommendations/${id}/decision`,{method:'PATCH',body:JSON.stringify({status,decision_note})}),
 alerts:(id)=>request(`/api/v1/alerts/${encodeURIComponent(id)}`)
};
