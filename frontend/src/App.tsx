import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Affiliates from './pages/Affiliates'
import Campaigns from './pages/Campaigns'
import Metrics from './pages/Metrics'
import Financial from './pages/Financial'
import Import from './pages/Import'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/affiliates" element={<Affiliates />} />
        <Route path="/campaigns" element={<Campaigns />} />
        <Route path="/metrics" element={<Metrics />} />
        <Route path="/financial" element={<Financial />} />
        <Route path="/import" element={<Import />} />
      </Route>
    </Routes>
  )
}
