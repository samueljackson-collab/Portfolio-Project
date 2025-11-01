import { useEffect, useState } from 'react'
import axios from './lib/api'
export default function App(){
  const [status,setStatus]=useState('loading')
  useEffect(()=>{ axios.get('/health').then(res=>setStatus(res.data.status)).catch(()=>setStatus('down')) },[])
  return <main style={{padding:24}}><h1>Portfolio Frontend</h1><p>API status: {status}</p></main>
}
